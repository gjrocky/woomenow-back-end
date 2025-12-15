import logging
from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.main.helper import email_dict
from apps.main.models import EmailExecution, Restaurant
from apps.snippet.models import EmailTemplateChoice, EmailTemplate
from send_custom_email import send_db_email

logger = logging.getLogger(__name__)


@shared_task
def send_restaurant_email_step(execution_uuid, step_number):
    logger.info(f"[Task Start] Step {step_number} | execution_id={execution_uuid}")

    with transaction.atomic():
        execution = (
            EmailExecution.objects
            .select_for_update()
            .filter(execution_id=execution_uuid, is_active=True)
            .first()
        )
        if not execution:
            logger.warning(f"[Step {step_number}] No active execution or automation stopped by admin.")
            return

        # Guard against duplicate Celery executions for the same step
        if execution.current_step >= step_number:
            logger.info(
                f"[Step {step_number}] Already processed (current_step={execution.current_step}). Skipping. "
            )
            return

        logger.info(f"[Step {step_number}] Current step={execution.current_step}, "
                    f"is_active={execution.is_active}, is_opened={execution.is_opened}")

        # Get all templates for the flow
        flow_slug = 'restaurant-and-experience-onboarding-playbook'
        templates = list(
            EmailTemplate.objects.filter(template__category__slug=flow_slug)
            .order_by('template__choice_id')
        )

        # Find index of last sent template (manual 1a or 1b)
        try:
            last_index = next(
                i for i, t in enumerate(templates) if t.template.choice_id == execution.last_sent_template_id)
        except StopIteration:
            logger.error(f"[Task] Last sent template ID {execution.last_sent_template_id} not found in DB")
            execution.is_active = False
            execution.save()
            return

        logger.info(
            f"[Task] Last sent template: '{templates[last_index].name}' | DB Index {templates[last_index].template.choice_id}")

        # Step 2 logic: wait for CTA
        if step_number == 2:
            wait_seconds = 24 * 60 * 60  # testing: 1 min; production: 24*60*60
            elapsed_seconds = (timezone.now() - execution.last_sent_at).total_seconds() if execution.last_sent_at else 0

            if elapsed_seconds < wait_seconds:
                remaining = wait_seconds - elapsed_seconds
                logger.info(f"[Step 2] Waiting for CTA window. Re-scheduling in {remaining} seconds.")
                send_restaurant_email_step.apply_async(
                    args=(execution_uuid, step_number),
                    countdown=remaining
                )
                return

            if execution.is_opened:
                # CTA clicked → send Email 2
                email_2_template = next((t for t in templates if t.template.choice_id == 3), None)
                if email_2_template:
                    execution.is_active = False
                    execution.current_step = step_number
                    execution.last_sent_at = timezone.now()
                    execution.save()
                    try:
                        logger.info(
                            f"[Debug] Passing to send_db_email (Email 2): {email_2_template.template} ({type(email_2_template.template)})")
                        send_db_email([execution.recipient_email], email_2_template.template,
                                      {"username": execution.recipient_name, **email_dict})
                        logger.info(f"[Step 2] CTA clicked → Email 2 sent: '{email_2_template.name}' (DB Index 3)")
                    except Exception as e:
                        logger.error(f"[Step 2] Failed to send Email 2: {e}")
                else:
                    logger.error("[Step 2] Email 2 template not found in DB")
                return
            else:
                # CTA not clicked → start drip sequence from DB index 4 onward
                drip_templates = [t for t in templates if t.template.choice_id >= 4]
                logger.info(
                    f"[Step 2] CTA not clicked → Starting drip sequence from DB Index {drip_templates[0].template.choice_id if drip_templates else 'N/A'}")
                step_number = 3
        else:
            # Drip step (step_number >= 3)
            drip_templates = [t for t in templates if t.template.choice_id >= 4]

        # Determine next template in drip sequence
        if execution.last_sent_template_id:
            try:
                last_drip_index = next(
                    i for i, t in enumerate(drip_templates) if t.template.choice_id == execution.last_sent_template_id)
                next_index = last_drip_index + 1
            except StopIteration:
                next_index = 0
        else:
            next_index = 0

        if next_index < len(drip_templates):
            template_to_send = drip_templates[next_index]

            # Update execution
            execution.last_sent_template_id = template_to_send.template.choice_id
            execution.current_step = step_number
            execution.last_sent_at = timezone.now()
            execution.save()

            # Send the drip email
            try:
                logger.info(
                    f"[Debug] Passing to send_db_email: {template_to_send.template} ({type(template_to_send.template)})")
                send_db_email([execution.recipient_email], template_to_send.template,
                              {"username": execution.recipient_name, **email_dict})
                logger.info(
                    f"[Step {step_number}] Drip email sent: '{template_to_send.name}' | DB Index {template_to_send.template.choice_id}")
            except Exception as e:
                logger.error(f"[Step {step_number}] Failed to send drip email: {e}")
                execution.is_active = False
                execution.current_step = step_number
                execution.last_sent_at = timezone.now()
                execution.save()
                return

            # Schedule next drip step if any
            if next_index + 1 < len(drip_templates):
                next_step_number = step_number + 1
                countdown_seconds = 24 * 60 * 60  # testing: 1 min; production: 24*60*60
                logger.info(
                    f"[Step {step_number}] Scheduling next drip step {next_step_number} in {countdown_seconds}s")
                send_restaurant_email_step.apply_async(args=(execution_uuid, next_step_number),
                                                       countdown=countdown_seconds)
            else:
                execution.is_active = False
                execution.save()
                logger.info(f"[Step {step_number}] Last drip email reached. Execution marked inactive.")
        else:
            # Step out of range → end execution
            execution.is_active = False
            execution.save()
            logger.info(f"[Step {step_number}] Step out of range. Execution marked inactive.")


@shared_task
def send_negative_reviews_email_step(execution_id, step_number, restaurant_id, automation_end_time):
    logger.info(f"[Negative Review Step {step_number}] Started for execution_id={execution_id}")

    with transaction.atomic():
        execution = EmailExecution.objects.select_for_update().filter(execution_id=execution_id, is_active=True).first()
        if not execution:
            logger.warning(
                f"[Negative Review Step {step_number}] No active execution found for execution_id={execution_id}")
            return

        # Prevent duplicate sends if Celery re-runs the same step
        if execution.current_step >= step_number:
            logger.info(
                f"[Negative Review Step {step_number}] Already processed (current_step={execution.current_step}). Skipping."
            )
            return

        # If the offer was already given, stop automation and do not send this step
        if execution.is_opened:
            logger.info(
                f"[Negative Review Step {step_number}] Offer already given for execution_id={execution_id}. Skipping step.")
            execution.is_active = False
            execution.save()
            return

        if step_number > 5:
            logger.info(f"[Negative Review Step {step_number}] Step exceeds limit (5). Marking execution inactive.")
            execution.is_active = False
            execution.save()
            return

        if automation_end_time is None:
            automation_end_time = timezone.now() + timedelta(minutes=(5 - step_number + 1))
        elif isinstance(automation_end_time, str):
            automation_end_time = timezone.localtime(timezone.datetime.fromisoformat(automation_end_time))

        countdown_seconds = 24 * 60 * 60  # production: 24*60*60 for 24h
        expected_execution_time = timezone.now() + timedelta(seconds=countdown_seconds)
        logger.info(
            f"[Negative Review Step {step_number}] Expected execution time for this step: {expected_execution_time}")
        logger.info(
            f"[Negative Review Step {step_number}] Automation end time (step 5): {timezone.localtime(automation_end_time)}")

        try:
            template_choice = EmailTemplateChoice.objects.filter(
                category__slug="negative-review-flow",
                choice_id=step_number
            ).first()

            if not template_choice:
                logger.info(f"[Negative Review Step {step_number}] Template not found. Ending execution.")
                execution.is_active = False
                execution.save()
                return

            restaurant = Restaurant.objects.filter(id=restaurant_id).first()
            if not restaurant:
                logger.error(
                    f"[Negative Review Step {step_number}] Restaurant not found for execution_id={execution_id}")
                return

            context_data = {
                "business_name": execution.recipient_name,
                "restaurant": restaurant.id,
                "insert_time": automation_end_time.strftime("%d %b %Y"),
                **email_dict,
            }

            # Update Execution
            execution.current_step = step_number
            execution.last_sent_at = timezone.now()
            execution.last_sent_template_id = template_choice.choice_id
            execution.execution_flow = "negative-review-flow"
            execution.save()

            send_db_email([restaurant.email], template_choice, context_data, execution_id)
            logger.info(
                f"[Negative Review Step {step_number}] Email sent to {restaurant.email} using {template_choice.label}")

        except Exception as e:
            logger.error(f"[Negative Review Step {step_number}] Failed to send email: {e}")
            return

        # Schedule next step
        next_step = step_number + 1

        if next_step == 4 and not execution.is_opened:
            logger.info(f"[Negative Review Step {step_number}] Skipping step 4 (4a email) as offer not given.")
            next_step = 5  # move directly to step 5

        if next_step <= 5:
            logger.info(f"[Negative Review Step {step_number}] Scheduling step {next_step} in {countdown_seconds}s")
            send_negative_reviews_email_step.apply_async(
                args=(str(execution.execution_id), next_step, restaurant_id, automation_end_time.isoformat()),
                countdown=countdown_seconds
            )
        else:
            logger.info(
                f"[Negative Review Step {step_number}] Last step reached. Automation complete at {automation_end_time}")
            execution.is_active = False
            execution.save()

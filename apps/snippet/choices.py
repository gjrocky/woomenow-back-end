from django.db import models
from django.utils.translation import gettext_lazy as _

EMAIL_TEMPLATE_CATEGORIES = (
    ('Onboarding Flow', (
        ('welcome_for_user', _('Welcome For User')),
        ('welcome_for_rest_exp', _('Welcome For Restaurant/Experience')),
        ('welcome_influ_join_community', _('Welcome Influencer for joining the community')),
        ('experience_get_email_to_onboard', _('Experience Get an Email to Onboard')),
        ('rest_email_to_onboard', _('Restaurant gets an Email to Onboard')),
        ('help_people_reconnect', _('Help People Reconnect You are selected to join WooMeNow')),
        ('invited_for_free_influ_video_shoot', _('You have been invited for Free Influence Video Shoot')),
        ('become_influencer', _('Become an influencer'))
    )),
    ('Engagement / Activation Flow', (
        ('final_call_influ_video_shoot', _('Final Call your no risk Influencer Video Shoot')),
        ('get_you_featured', _('Get You Featured')),
        ('get_offer_from_rest', _('Get an Offer From Restaurant')),
        ('join_the_woo', _('Join The Woo')),
        ('just_checking_excited_to_collaborate', _('Just Checking in Excited to possibly Collaborate')),
        ('handpicked_to_help_people_reconnect', _('You have been Handpicked To Help People Reconnect')),
        ('your_woomenow_shoot_is_coming', _('Your WooMeNow shoot is coming what to expect')),
        ('thanks_part_of_woomenow_movement', _('Thanks for being Part of WooMeNow Movement'))
    )),
    ('Review / UGC Notification Flow', (
        ('bad_review', _('Bad Review for Restaurant/Experience')),
        ('receive_review_for_approval_influencer', _('Receive Review for Approval Influencer'))
    )),
    ('Password / Account Flow', (
        ('reset', _('Reset')),
        ('reset_your_password', _('Reset Your Password')),
        ('resend', _('Resend')),
        ('confirmation', _('Confirmation')),
        ('contact_us', _('Contact Us')),
        ('your_password_has_been_changed', _('Yours Password Has Been Changed'))
    ))
)


class EmailTemplateType(models.TextChoices):
    BAD_REVIEW = 'bad_review', _('Bad Review for Restaurant/Experience')
    BECOME_INFLUENCER = 'become_influencer', _('Become an influencer')
    BOOK_RESERVATION_REST = 'book_reservation_rest', _('Book a Reservation Restaurant')
    WELCOME_FOR_USER = 'welcome_for_user', _('Welcome For User')
    BOOK_RESERVATION_USER = 'book_reservation_user', _('Book a Reservation User')
    CONFIRMATION = 'confirmation', _('Confirmation')
    CONTACT_US = 'contact_us', _('Contact Us')
    EXPERIENCE_GET_EMAIL_TO_ONBOARD = 'experience_get_email_to_onboard', _('Experience Get an Email to Onboard')
    FINAL_CALL_INFLU_VIDEO_SHOOT = 'final_call_influ_video_shoot', _('Final Call your no risk Influencer Video Shoot')
    GET_YOU_FEATURED = 'get_you_featured', _('Get You Featured')
    GET_OFFER_FROM_REST = 'get_offer_from_rest', _('Get an Offer From Restaurant')
    HELP_PEOPLE_RECONNECT = 'help_people_reconnect', _('Help People Reconnect You are selected to join WooMeNow')
    JOIN_THE_WOO = 'join_the_woo', _('Join The Woo')
    JUST_CHECKING_EXCITED_TO_COLLABORATE = 'just_checking_excited_to_collaborate', _(
        'Just Checking in Excited to possibly Collaborate')
    RECEIVE_REVIEW_FOR_APPROVAL_INFLUENCER = 'receive_review_for_approval_influencer', _(
        'Receive Review for Approval Influencer')
    RESEND = 'resend', _('Resend')
    RESET = 'reset', _('Reset')
    RESET_YOUR_PASSWORD = 'reset_your_password', _('Reset Your Password')
    REST_EMAIL_TO_ONBOARD = 'rest_email_to_onboard', _('Restaurant gets an Email to Onboard')
    THANKS_PART_OF_WOOMENOW_MOVEMENT = 'thanks_part_of_woomenow_movement', _(
        'Thanks for being Part of WooMeNow Movement')
    WELCOME_FOR_REST_EXP = 'welcome_for_rest_exp', _('Welcome For Restaurant/Experience')
    WELCOME_INFLU_JOIN_COMMUNITY = 'welcome_influ_join_community', _('Welcome Influencer for joining the community')
    HANDPICKED_TO_HELP_PEOPLE_RECONNECT = 'handpicked_to_help_people_reconnect', _(
        'You have been Handpicked To Help People Reconnect')
    INVITED_FOR_FREE_INFLU_VIDEO_SHOOT = 'invited_for_free_influ_video_shoot', _(
        'You have been invited for Free Influence Video Shoot')
    YOUR_PASSWORD_HAS_BEEN_CHANGED = 'your_password_has_been_changed', _('Yours Password Has Been Changed')
    YOUR_WOOMENOW_SHOOT_IS_COMING = 'your_woomenow_shoot_is_coming', _('Your WooMeNow shoot is coming what to expect')

import json
import os

from django.conf import settings
from django.core.files import File
from wagtail.images.models import Image
from wagtail.models import Page

from apps.main.models import About, Business, FAQs, Pricing, JoinTheWoo, Influencer, Restaurant
from apps.snippet.models import State, City, Category, Ambience, Contact, IPLocation
from apps.users.models import User

with open('apps/main/fixtures/state.json', 'r', encoding='utf-8') as f:
    states = json.loads(f.read())
with open('apps/main/fixtures/categories.json', 'r', encoding='utf-8') as f:
    categories = json.loads(f.read())
with open('apps/main/fixtures/ambience.json', 'r', encoding='utf-8') as f:
    ambiences = json.loads(f.read())
with open('apps/main/fixtures/about.json', 'r', encoding='utf-8') as f:
    about = json.loads(f.read())
with open('apps/main/fixtures/business.json', 'r', encoding='utf-8') as f:
    business = json.loads(f.read())
with open('apps/main/fixtures/faqs.json', 'r', encoding='utf-8') as f:
    Faqs = json.loads(f.read())
with open('apps/main/fixtures/jointhewoo.json', 'r', encoding='utf-8') as f:
    jointhewoo = json.loads(f.read())
with open('apps/main/fixtures/pricing.json', 'r', encoding='utf-8') as f:
    pricing = json.loads(f.read())
with open('apps/main/fixtures/influencers.json', 'r', encoding='utf-8') as f:
    influencers = json.loads(f.read())
with open('apps/main/fixtures/restaurants.json', 'r', encoding='utf-8') as f:
    restaurants = json.loads(f.read())
with open('apps/main/fixtures/campain.json', 'r', encoding='utf-8') as f:
    campaigns = json.loads(f.read())
with open('apps/main/fixtures/contact-form.json', 'r', encoding='utf-8') as f:
    contact_form = json.loads(f.read())
with open('apps/main/fixtures/iplocation.json', 'r', encoding='utf-8') as f:
    iplocation = json.loads(f.read())


def get_image(img, id=None):
    img_path = os.path.join(settings.BASE_DIR, *img.split('/'))
    with open(img_path, "rb") as f:
        image = Image(title=img.split('/')[-1], file=File(f))
        image.save()
    if not id:
        return image.id
    return image


def create_states():
    for s in states:
        state = State()
        state.name = s['name']
        state.ISO_code = s['ISO_code']
        state.save()
        for c in s['cities']:
            city = City()
            city.name = c['name']
            city.state = state
            city.save()


def create_categories():
    for c in categories:
        category = Category()
        category.name = c['fields']['name']
        category.image = get_image(c['fields']['image'], id=True)
        category.save()


def create_ambience():
    for a in ambiences:
        ambience = Ambience()
        ambience.name = a['name']
        ambience.save()


def create_about():
    root_page = Page.get_first_root_node()
    a = About()
    a.title = 'About'
    a.heading = about['heading']
    a.description = about['description']
    a.vision_title = about['vision_title']
    existing_stream_data = a.vision_points or []
    for vision_point in about['vision_points']:
        existing_stream_data.append(
            {"type": "mission_and_vision",
             "value": {"heading": vision_point['heading'],
                       "description": vision_point['description'],
                       "image": get_image(vision_point['img'])
                       }
             }
        )

    a.vision_points = existing_stream_data
    root_page.add_child(instance=a)
    root_page.save()
    a.save()
    a.save_revision().publish()


def create_business():
    root_page = Page.get_first_root_node()
    b = Business()
    b.title = 'Business'
    b.heading = business['heading']
    b.description = business['description']
    b.CTA_btn = business['CTA_btn']
    key_point = b.key_point or []
    for k in business['key_point']:
        key_point.append(
            {"type": "key_point",
             "value": {"value": k['value'],
                       "text": k['text'],
                       }
             }
        )
    b.key_point = key_point
    b.choose_heading = business['choose_heading']
    b.choose_description = business['choose_description']
    why_choose_us_cards = b.why_choose_us_cards or []
    for card in business['why_choose_us_cards']:
        why_choose_us_cards.append({"type": "cards",
                                    "value": {"heading": card['heading'],
                                              "description": card['description'],
                                              }
                                    })
    b.why_choose_us_cards = why_choose_us_cards
    b.win_plan_heading = business['win_plan_heading']
    b.win_plan_description = business['win_plan_description']
    win_plan_cards = b.win_plan_cards or []
    for card in business['win_plan_cards']:
        win_plan_cards.append({"type": "cards",
                               "value": {"heading": card['heading'],
                                         "description": card['description'],
                                         "image": get_image(card['img'])

                                         }
                               })
    b.win_plan_cards = win_plan_cards
    b.price_heading = business['price_heading']
    b.price_description = business['price_description']
    b.price_btn = business['price_btn']
    faqs = b.faq or []
    for f in business['faqs']:
        faqs.append({"type": "que_and_ans",
                     "value": {"que": f['que'],
                               "ans": f['ans'],
                               }
                     })
    b.faq = faqs
    root_page.add_child(instance=b)
    root_page.save()
    b.save()
    b.save_revision().publish()


def create_faqs():
    root_page = Page.get_first_root_node()
    f = FAQs()
    f.title = 'FAQs'
    faqs = f.faq or []
    for ff in Faqs:
        faqs.append({"type": "que_and_ans",
                     "value": {"que": ff['que'],
                               "ans": ff['ans'],
                               }
                     })
    f.faq = faqs
    root_page.add_child(instance=f)
    root_page.save()
    f.save()
    f.save_revision().publish()


def create_jointhewoo():
    root_page = Page.get_first_root_node()
    j = JoinTheWoo()
    j.title = 'Join The Woo'
    j.heading = jointhewoo['heading']
    j.description = jointhewoo['description']
    j.about_community = jointhewoo['about_community']
    j.sub_heading = jointhewoo['sub_heading']
    community_points = j.community_points or []
    for point in jointhewoo['community_points']:
        community_points.append({"type": "point",
                                 "value": point.get('point', '')
                                 })
    j.community_points = community_points
    root_page.add_child(instance=j)
    root_page.save()
    j.save()
    j.save_revision().publish()


def create_pricing():
    root_page = Page.get_first_root_node()
    p = Pricing()
    p.title = 'Pricing'
    p.heading = pricing['heading']
    p.description = pricing['description']
    p.note = pricing['note']
    p.CTA_btn = pricing['CTA_btn']
    cards = p.cards or []
    for card in pricing['cards']:
        points = []
        for point in card['points']:
            points.append({"type": "points",
                           "value": point.get('points', '')
                           })
        cards.append({"type": "cards",
                      "value": {"heading": card['heading'],
                                "description": card['description'],
                                "price": card['price'],
                                "extra": card['extra'],
                                "saving": card['saving'],
                                "points": points,
                                }
                      })
    p.cards = cards
    root_page.add_child(instance=p)
    root_page.save()
    p.save()
    p.save_revision().publish()


def create_influencer():
    root_page = Page.get_first_root_node()
    for influencer in influencers:
        city = City.objects.get(name__icontains=influencer['influencer']['city'].lower())
        user = User.objects.create_user(
            email=influencer['user']['email'],
            password=settings.ADMIN_PASSWORD,
            first_name=influencer['user']['first_name'],
            last_name=influencer['user']['last_name'],
            is_active=True,
            city=city,
        )
        user.save()
        i = Influencer()
        i.title = influencer['influencer']['name']
        i.user = user
        i.name = influencer['influencer']['name']
        i.description = influencer['influencer']['description']
        i.profile = get_image(influencer['influencer']['profile'], id=True)
        i.city = city
        social_links = i.social_links or []
        for link in influencer['influencer']['social_links']:
            social_links.append({"type": "link",
                                 "value": link
                                 })
        i.social_links = social_links
        root_page.add_child(instance=i)
        root_page.save()
        i.save()
        i.save_revision().publish()


def create_superuser():
    user = User.objects.create_superuser(
        email=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
        first_name='anthony',
        last_name='untaran',
        is_active=True,
        is_superuser=True,
        is_staff=True,
    )
    user.save()


def create_res():
    user = User.objects.get(email='anthony.untaran@gmail.com')
    root_page = Page.get_first_root_node()
    for res in restaurants:
        r = Restaurant()
        r.title = res['title']
        r.slug = res['slug']
        r.name = res['name']
        r.short_description = res['short_description']
        r.phone_number = res['phone_number']
        r.location = res['location']
        r.type = res['type']
        r.is_featured = res['is_featured']
        r.is_home_featured = res['is_home_featured']
        r.website_url = res['website_url']
        r.email = res['email']
        r.user = user
        r.budget_friendly = res['budget_friendly']
        r.reservation_time = res['reservation_time']
        city = City.objects.get(name__icontains=res['city'].lower())
        r.city = city
        r.recommended_by = User.objects.filter(influencer__name__in=res['recommended_by'])
        r.categories = Category.objects.filter(name__in=res['categories'])
        images = r.restaurant_images or []
        for img in res['restaurant_images']:
            images.append({"type": "image",
                           "value": get_image(img)
                           })
        r.restaurant_images = images
        root_page.add_child(instance=r)
        root_page.save()
        r.save()
        r.save_revision().publish()


def create_contact_form():
    for contact in contact_form:
        c = Contact()
        c.name = contact['fields']['form_data']['name']
        c.email = contact['fields']['form_data']['email']
        c.phone = contact['fields']['form_data']['number']
        c.subject = contact['fields']['form_data'].get('subject', '')
        c.message = contact['fields']['form_data'].get('description', '')
        c.save()


def create_campaign():
    pass


def create_iplocation():
    for campaign in iplocation:
        if not campaign['fields'].get('ip_address'):
            continue
        c = IPLocation()
        c.ip_address = campaign['fields']['ip_address']
        c.city = campaign['fields'].get('city', '')
        c.state = campaign['fields'].get('state', '')
        c.country = campaign['fields'].get('country', '')
        c.ISO = campaign['fields'].get('ISO', '')
        c.extra = campaign['fields'].get('extra', {})
        c.save()


def create_data():
    create_superuser()
    create_states()
    create_categories()
    create_ambience()
    create_about()
    create_business()
    create_faqs()
    create_jointhewoo()
    create_pricing()
    create_influencer()
    create_res()
    create_contact_form()
    create_iplocation()
    create_campaign()

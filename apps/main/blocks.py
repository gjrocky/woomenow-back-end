from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class FAQS(blocks.StructBlock):
    que = blocks.RichTextBlock(required=True)
    ans = blocks.RichTextBlock(required=True)


class KeyPoint(blocks.StructBlock):
    value = blocks.TextBlock(required=True, max_length=10, help_text='Block Value')
    text = blocks.RichTextBlock(required=True, max_length=150, help_text='Block Description')


class WhyChooseUsCards(blocks.StructBlock):
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text="Block Title")
    description = blocks.RichTextBlock(
        required=True, max_length=350, help_text="Block Description"
    )


class WinPlanCards(blocks.StructBlock):
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text="Block Title")
    description = blocks.RichTextBlock(
        required=True, max_length=255, help_text="Block Description"
    )
    image = ImageChooserBlock(required=True)


class OurMissionVision(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text='Block Title')
    description = blocks.RichTextBlock(required=True, max_length=150, help_text='Block Description')


class PricingCard(blocks.StructBlock):
    heading = blocks.TextBlock(required=True, max_length=50, help_text='Heading')
    description = blocks.TextBlock(required=True, max_length=255, help_text='Description')
    price = blocks.TextBlock(required=False, max_length=50, help_text='Price')
    extra = blocks.TextBlock(required=False, max_length=500, help_text='Extra Description')
    saving = blocks.RichTextBlock(required=False, max_length=500, help_text='Savings Description')
    strike_through = blocks.RichTextBlock(required=False, max_length=500, help_text='Strike through')
    points = blocks.StreamBlock([
        ("points", blocks.RichTextBlock(required=True, max_length=500)),
    ])


class ReadyToElevateBlock(blocks.StructBlock):
    heading = blocks.RichTextBlock(required=True, max_length=500, help_text='Heading')
    description = blocks.RichTextBlock(required=True, max_length=2000, help_text='Description')
    cta_button = blocks.RichTextBlock(required=True, max_length=200, help_text='Cta Button')
    cta_button_link = blocks.URLBlock(required=True, max_length=2000, help_text='Cta Button Link')
    section_image = ImageChooserBlock(required=True, help_text="Section Image")


class TermsOfServiceBlock(blocks.StructBlock):
    id = blocks.IntegerBlock(required=True, help_text='Condition Number')
    heading = blocks.RichTextBlock(required=True, help_text='Heading')
    content = blocks.RichTextBlock(required=True, help_text='Content')


class PrivacyPolicyBlock(blocks.StructBlock):
    id = blocks.IntegerBlock(required=True, help_text='Policy Number')
    heading = blocks.RichTextBlock(required=True, help_text='Heading')
    content = blocks.RichTextBlock(required=True, help_text='Content')


class DiamondStatusBlock(blocks.StructBlock):
    title = blocks.RichTextBlock(required=True, help_text='Title')
    description = blocks.RichTextBlock(required=True, help_text='Description')


class ReviewSystemBlock(blocks.StructBlock):
    title = blocks.RichTextBlock(required=True, help_text='Title')
    description = blocks.RichTextBlock(required=True, help_text='Description')

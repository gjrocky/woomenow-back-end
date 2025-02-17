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
    description = blocks.TextBlock(required=True, max_length=50, help_text='Description')
    price = blocks.TextBlock(required=False, max_length=50, help_text='Price')
    extra = blocks.TextBlock(required=False, max_length=500, help_text='Extra Description')
    saving = blocks.TextBlock(required=False, max_length=500, help_text='Savings Description')
    points = blocks.StreamBlock([
        ("points", blocks.RichTextBlock(required=True, max_length=500)),
    ])




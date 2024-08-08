from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class FAQS(blocks.StructBlock):
    que = blocks.RichTextBlock(required=True)
    ans = blocks.RichTextBlock(required=True)


class KeyPoint(blocks.StructBlock):
    value = blocks.TextBlock(required=True, max_length=10, help_text='Block Value')
    text = blocks.RichTextBlock(required=True, max_length=150, help_text='Block Description')


class WhyChooseUsCards(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text="Block Title")
    description = blocks.RichTextBlock(
        required=True, max_length=350, help_text="Block Description"
    )


class WinPlanCards(blocks.StructBlock):
    icon = ImageChooserBlock(required=True)
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text="Block Title")
    description = blocks.RichTextBlock(
        required=True, max_length=150, help_text="Block Description"
    )
    image = ImageChooserBlock(required=True)


class OurMissionVision(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    heading = blocks.RichTextBlock(required=True, max_length=50, help_text='Block Title')
    description = blocks.RichTextBlock(required=True, max_length=150, help_text='Block Description')

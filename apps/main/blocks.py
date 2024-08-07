from wagtail import blocks


class FAQS(blocks.StructBlock):
    que = blocks.RichTextBlock(required=True)
    ans = blocks.RichTextBlock(required=True)

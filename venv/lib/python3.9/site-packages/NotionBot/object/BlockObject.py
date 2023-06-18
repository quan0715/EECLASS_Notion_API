from ..object import *
from typing import Union


class BaseBlockObject:
    def __init__(self, block_type, color=Colors.Text.default, text_block=None, children=None):
        self.block_type = block_type
        self.template = {"type": self.block_type, self.block_type: {}}
        self.color = color
        self.children = children
        self.default_text = f"{self.block_type}"
        self.text_block = text_block

    def make(self):
        return self.template

    def update_file(self, file):
        if isinstance(file, str):
            file = FileValue(file)
        if isinstance(file, FileValue):
            self.template[self.block_type] = file.make()

    @classmethod
    def rich_text(cls, text_block):
        return {"rich_text": [text.make() for text in text_block]}

    @classmethod
    def caption(cls, text_block):
        return {"caption": [text_block.make()]}

    def update_color(self, color):
        self.template[self.block_type].update(dict(color=color))

    def update_text(self, text_block):
        if not len(text_block):
            self.text_block = [TextBlock(self.default_text)]
        text_block = []
        for i in range(len(self.text_block)):
            if isinstance(self.text_block[i], str):
                text_block.append(TextBlock(content=str(self.text_block[i])))
            else:
                text_block.append(self.text_block[i])

        self.template[self.block_type].update(self.rich_text(text_block))

    def update_children(self, children):
        if isinstance(children, list):
            children = Children(*children)
        if isinstance(children, Children):
            self.template[self.block_type].update(children.make())


class TextBlock(BaseBlockObject):
    @classmethod
    def check_length_and_split(cls, target: str):
        if len(target) > 1999:
            s, e, k = 0, 2000, 0
            return [
                target[s+k:e+k] for k in range(0,len(target),2000)
            ]
        return False
    def __init__(self, content="This is Text", link=None, annotations=None):
        super().__init__(block_type="text", text_block=None)
        self.content = content
        self.link = link
        self.template[self.block_type] = {"content": self.content}
        if isinstance(link, str):
            self.template[self.block_type].update(dict(link=Link(self.link).template))
        if isinstance(annotations, dict):
            annotations = Annotations(**annotations)
        if isinstance(annotations, Annotations):
            self.template.update(annotations=annotations.make())


# class RichTextObject:
#     def __init__(self, *text_block: TextBlock):
#         self.template =

class ParagraphBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, children=None):
        super().__init__(block_type="paragraph", color=color, text_block=text_block, children=children)
        self.update_color(self.color)
        self.update_text(self.text_block)
        self.update_children(self.children)


class HeadingBlock(BaseBlockObject):
    def __init__(self, heading_level=1, *text_block, color=Colors.Text.default):
        self.heading_level = heading_level
        super().__init__(f"heading_{self.heading_level}", color=color, text_block=text_block)
        self.update_color(self.color)
        self.update_text(self.text_block)
        self.update_children(self.children)


class CallOutBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, emoji=None, children=None):
        super().__init__("callout", color=color, text_block=text_block, children=children)
        self.emoji = emoji
        if isinstance(emoji, str):
            self.template[self.block_type] = dict(icon=Emoji(self.emoji).make())
        self.update_color(self.color)
        self.update_text(self.text_block)
        self.update_children(children)


class QuoteBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, children=None):
        super().__init__("quote", color=color, text_block=text_block, children=children)
        self.update_children(self.children)
        self.update_color(self.color)
        self.update_text(self.text_block)


class BulletedBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, children=None):
        super().__init__("bulleted_list_item", color=color, text_block=text_block, children=children)
        self.update_children(self.children)
        self.update_color(self.color)
        self.update_text(self.text_block)


class NumberedBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, children=None):
        super().__init__("numbered_list_item", color=color, text_block=text_block, children=children)
        self.update_children(self.children)
        self.update_color(self.color)
        self.update_text(self.text_block)


class ToDoBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, checked=False, children=None):
        super().__init__("to_do", color=color, text_block=text_block, children=children)
        self.update_children(self.children)
        self.update_color(self.color)
        self.update_text(self.text_block)
        self.check = checked
        self.template[self.block_type].update(dict(checked=checked))


class ToggleBlock(BaseBlockObject):
    def __init__(self, *text_block, color=Colors.Text.default, children=None):
        super().__init__("toggle", color=color, text_block=text_block, children=children)
        self.update_children(self.children)
        self.update_color(self.color)
        self.update_text(self.text_block)


class CodeBlock(BaseBlockObject):
    def __init__(self, *text_block, caption=None, color=Colors.Text.default, language="plain text", children=None):
        super().__init__("code", color=color, text_block=text_block, children=children)
        self.caption = caption
        if isinstance(self.caption, TextBlock):
            self.template[self.block_type].update(BaseBlockObject.caption(self.caption))
        self.update_children(self.children)
        self.update_text(self.text_block)
        self.language = language
        self.template[self.block_type].update(dict(language=language))


class ChildPageBlock(BaseBlockObject):
    def __init__(self, title="child_page"):
        super().__init__("child_page")
        self.title = title
        self.template[self.block_type] = dict(title=title)


class ChildDataBaseBlock(BaseBlockObject):
    def __init__(self, title="child_database"):
        super().__init__("child_database")
        self.title = title
        self.template[self.block_type] = dict(title=title)


class EmbedBlock(BaseBlockObject):
    def __init__(self, url):
        super().__init__("embed")
        self.url = url
        self.template[self.block_type] = dict(url=self.url)


class ImageBlock(BaseBlockObject):
    def __init__(self, file):
        super().__init__("image")
        self.file = file
        self.update_file(self.file)


class VideoBlock(BaseBlockObject):
    def __init__(self, file):
        super().__init__("video")
        self.file = file
        self.update_file(self.file)


class FileBlock(BaseBlockObject):
    def __init__(self, file=None):
        super().__init__("file")
        self.file = file
        self.update_file(self.file)


class PDFBlock(BaseBlockObject):
    def __init__(self, file):
        super().__init__("pdf")
        self.file = file
        self.update_file(self.file)


class BookmarkBlock(BaseBlockObject):
    def __init__(self, caption=None, url=None):
        super().__init__("bookmark")
        self.caption = caption
        self.url = url
        self.template[self.block_type].update(dict(url=self.url))
        if isinstance(self.caption, TextBlock):
            self.template[self.block_type].update(BaseBlockObject.caption(self.caption))


class EquationBlockObject(BaseBlockObject):
    def __init__(self, expression):
        super().__init__("equation")
        self.expression = expression
        self.template[self.block_type].update(dict(expression=self.expression))


class DividerBlock(BaseBlockObject):
    def __init__(self):
        super().__init__("divider")


class TableOfContentBlock(BaseBlockObject):
    # show an outline of content
    def __init__(self, color=Colors.Text.default):
        super().__init__("table_of_contents", color=color)


class BreadcrumbBlock(BaseBlockObject):
    def __init__(self):
        super().__init__("breadcrumb")


class ColumnListBlock(BaseBlockObject):
    # parent block for column children
    def __init__(self, children=None):
        super().__init__("column_list", children=children)
        self.update_children(self.children)


class ColumnBlock(BaseBlockObject):
    def __init__(self, children=None):
        super().__init__("column", children=children)
        self.update_children(self.children)


class LinkPreviewBlock(BaseBlockObject):
    # can't be create
    def __init__(self, url=None):
        super().__init__("link_preview")
        self.url = url


class TemplateBlock(BaseBlockObject):
    def __init__(self, *title, children=None):
        super().__init__("template", text_block=title, children=children)
        self.update_text(title)
        self.update_children(self.children)


class LinkToPageBlock(BaseBlockObject):
    def __init__(self, target):
        # page_id or database_id
        super().__init__("link_to_page")
        if isinstance(target, dict):
            target = Parent(target['type'], target['id'])
        if isinstance(target, Parent):
            self.template[self.block_type] = target.make()


class SyncedBlock(BaseBlockObject):
    def __init__(self, synced_from=None, children=None):
        super().__init__("synced_block", children=children)
        self.synced_from = synced_from
        if not self.synced_from:
            self.template[self.block_type].update(dict(synced_from=self.synced_from))
            self.update_children(self.children)
        else:
            self.template[self.block_type].update(dict(synced_from=dict(block_id=self.synced_from)))


class TableBlock(BaseBlockObject):
    def __init__(self, table_width=1, column_header=True, row_header=True, children=None):
        super().__init__("table", children=children)
        self.table_width = table_width
        self.column_header = column_header
        self.row_header = row_header
        self.update_children(self.children)
        self.template[self.block_type].update(
            dict(
                table_width=self.table_width,
                has_column_header=self.column_header,
                has_row_header=self.row_header,
            )
        )
        row_list = self.template[self.block_type]["children"]
        for row in row_list:
            cells = row['table_row']['cells']
            for i in range(self.table_width - len(cells)):
                row['table_row']['cells'].append([TextBlock("").make()])


class TableRowBlock(BaseBlockObject):
    def __init__(self, *cells):
        super().__init__("table_row")
        cell_list = []
        for cell in cells:
            if isinstance(cell, str):
                cell = TextBlock(content=cell)
            if isinstance(cell, TextBlock):
                cell_list.append([cell.make()])

        self.template[self.block_type].update(dict(cells=cell_list))

# class Blocks:
#     Paragraph = ParagraphBlock
#     Heading = HeadingBlock
#     Code = CodeBlock
#     Toggle = ToggleBlock
#     Numbered = NumberedBlock
#     Bulleted = BulletedBlock
#     ToDoList = ToDoBlock
#     Callout = CalloutBlock
#     Quote = QuoteBlock
#     Text = TextBlock
#     Embed = EmbedBlock
#     Image = ImageBlock
#     Video = VideoBlock
#     PDF = PDFBlock
#     Bookmark = BookmarkBlock
#     Equation = EquationBlock
#     Divider = DividerBlock
#     FileValue = FileBlockObject
#     TableOfContent = TableOfContentBlock
#     Breadcrumb = BreadcrumbBlock
#     ColumnList = ColumnListBlock
#     ColumnBlock = ColumnBlock
#     Template = TemplateBlock
#     LinkToPage = LinkToPageBlock
#     Synced = SyncedBlock
#     TableRow = TableRowBlock
#     Table = TableBlock

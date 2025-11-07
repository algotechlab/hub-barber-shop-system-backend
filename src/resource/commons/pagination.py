from dataclasses import dataclass, field, fields

from flask_restx import reqparse


@dataclass
class PaginationArguments:
    current_page: int = field(default=1, metadata={"help": "Current Page"})
    rows_per_page: int = field(default=10, metadata={"help": "Rows per Page"})
    order_by: str = field(default="", metadata={"help": "Order By"})
    sort_by: str = field(default="", metadata={"help": "Sort By"})
    filter_by: str = field(default="", metadata={"help": "Filter By"})

    @classmethod
    def add_to_parser(cls, parser: reqparse.RequestParser):
        for f in fields(cls):
            parser.add_argument(
                f.name,
                type=f.type,
                default=f.default,
                required=False,
                help=f.metadata.get("help", f.name.replace("_", " ").title()),
            )

    @classmethod
    def parse_from_request(cls):
        parser = reqparse.RequestParser()
        cls.add_to_parser(parser)
        args = parser.parse_args()
        return cls(**vars(args))

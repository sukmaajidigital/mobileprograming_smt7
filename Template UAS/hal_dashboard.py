from flet import *


def cycle_card(days, label):
    return Container(
        width=120,
        height=80,
        bgcolor="white",
        border_radius=12,
        padding=10,
        shadow=BoxShadow(blur_radius=10, color="black12"),
        content=Column(
            [
                Text(days, size=20, weight="bold"),
                Text(label, size=12, color="black54"),
            ],
            horizontal_alignment="center",
        ),
    )


def dashboard_view():
    return Container(
        padding=20,
        expand=True,
        content=Column(
            scroll="auto",
            spacing=20,
            controls=[
                _top_cards(),
                _charts(),
                _contract_table(),
                _bottom_section(),
            ],
        ),
    )


# ===================== SECTIONS =====================

def _top_cards():
    return Row(
        spacing=20,
        controls=[
            _stat_card("Accepted", "2,340", "#0f9d58"),
            _stat_card("In Contract", "1,782", "#f4b400"),
            _stat_card("In Approval", "1,596", "#db4437"),
        ],
    )


def _charts():
    return Row(
        spacing=20,
        controls=[
            _bar_chart(),
            _pie_chart(),
        ],
    )


def _bottom_section():
    return Row(
        spacing=20,
        controls=[
            _contract_type(),
            _average_cycle(),
        ],
    )


# ===================== COMPONENTS =====================

def _stat_card(title, value, color):
    return Container(
        expand=True,
        padding=15,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            [
                Text(title, weight="bold"),
                Text(value, size=32, weight="bold", color=color),
            ]
        ),
    )


def _bar_chart():
    return Container(
        expand=1,
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            spacing=10,
            controls=[
                Text("Contract by Stages", weight="bold"),
                BarChart(
                    bar_groups=[
                        BarChartGroup(
                            x=1,
                            bar_rods=[
                                BarChartRod(from_y=0, to_y=80, width=22, color="#0f9d58")
                            ],
                        ),
                        BarChartGroup(
                            x=2,
                            bar_rods=[
                                BarChartRod(from_y=0, to_y=40, width=22, color="#f4b400")
                            ],
                        ),
                        BarChartGroup(
                            x=3,
                            bar_rods=[
                                BarChartRod(from_y=0, to_y=60, width=22, color="#db4437")
                            ],
                        ),
                        BarChartGroup(
                            x=4,
                            bar_rods=[
                                BarChartRod(from_y=0, to_y=25, width=22, color="#5f6368")
                            ],
                        ),
                    ],
                    max_y=100,
                    height=250,
                ),
            ],
        ),
    )


def _pie_chart():
    return Container(
        expand=1,
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            horizontal_alignment="center",
            spacing=10,
            controls=[
                Text("Contract Expiring", weight="bold"),
                PieChart(
                    sections=[
                        PieChartSection(value=40, color="#0f9d58", title="60 days"),
                        PieChartSection(value=35, color="#f4b400", title="30 days"),
                        PieChartSection(value=25, color="#db4437", title="Expired"),
                    ],
                    height=230,
                    width=230,
                ),
            ],
        ),
    )


def _contract_table():
    return Container(
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            spacing=10,
            controls=[
                Text("My Contracts", size=20, weight="bold"),
                Divider(),
                Row(
                    [
                        Text("Serial #", expand=1, weight="bold"),
                        Text("Name", expand=2, weight="bold"),
                        Text("Value", expand=1, weight="bold"),
                        Text("Status", expand=1, weight="bold"),
                    ]
                ),
                Divider(),
                Row(
                    [
                        Text("CTR1000039F", expand=1),
                        Text("Horizon Tech", expand=2),
                        Text("$48,292", expand=1),
                        Container(
                            Text("Active", color="white"),
                            padding=6,
                            bgcolor="#0f9d58",
                            border_radius=6,
                        ),
                    ]
                ),
            ],
        ),
    )


def _contract_type():
    return Container(
        expand=1,
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            spacing=10,
            controls=[
                Text("Contract by Type", size=18, weight="bold"),
                Text("NDA"),
                Text("Insurance"),
                Text("Lease"),
                Text("Sale"),
            ],
        ),
    )


def _average_cycle():
    return Container(
        expand=1,
        padding=20,
        bgcolor="white",
        border_radius=12,
        shadow=BoxShadow(blur_radius=12, color="black12"),
        content=Column(
            spacing=15,
            controls=[
                Text("Average Cycle Time", size=18, weight="bold"),
                Row(
                    spacing=15,
                    controls=[
                        cycle_card("25 days", "NDA"),
                        cycle_card("45 days", "Insurance"),
                        cycle_card("18 days", "Lease"),
                    ],
                ),
            ],
        ),
    )

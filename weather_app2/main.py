import flet as ft
from api import fetch_area_list, fetch_forecast
from db import init_db, insert_forecast, get_forecast_by_area


def main(page: ft.Page):
    init_db()

    page.title = "天気予報アプリ（DB対応）"
    page.theme_mode = ft.ThemeMode.LIGHT

    forecast_view = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)

    def on_area_click(area_code):
        forecast_view.controls.clear()

        # API取得
        data = fetch_forecast(area_code)
        series = data[0]["timeSeries"][0]

        times = series["timeDefines"]
        weathers = series["areas"][0]["weathers"]

        # APIで取ったデータを DB に保存
        for t, w in zip(times, weathers):
            insert_forecast(area_code, t[:10], w)

        # DBから取得して表示
        rows = get_forecast_by_area(area_code)

        for date, weather in rows:
            forecast_view.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=10,
                        content=ft.Column([
                            ft.Text(date, weight="bold"),
                            ft.Text(weather)
                        ])
                    )
                )
            )

        page.update()

    area_json = fetch_area_list()
    centers = area_json["centers"]
    offices = area_json["offices"]

    region_controls = []

    for center_code, center_info in centers.items():
        children = center_info.get("children", [])

        tiles = []
        for office_code in children:
            if office_code in offices:
                office_name = offices[office_code]["name"]
                tiles.append(
                    ft.ListTile(
                        title=ft.Text(office_name),
                        on_click=lambda e, code=office_code: on_area_click(code)
                    )
                )

        if tiles:
            region_controls.append(
                ft.ExpansionTile(
                    title=ft.Text(center_info["name"]),
                    controls=tiles
                )
            )

    rail = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCATION_ON,
                label="地域"
            )
        ],
        extended=True,
        leading=ft.Column(region_controls, scroll=ft.ScrollMode.AUTO),
        expand=True
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                ft.Container(
                    expand=True,
                    padding=20,
                    content=forecast_view
                )
            ]
        )
    )


ft.app(target=main)



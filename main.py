import flet as ft
from db import create_tables, get_scripts, add_script_to_db, run_script_from_db, delete_script_from_db


# Основная логика Flet приложения
def main(page: ft.Page):
    # Инициализация UI компонентов
    neon_color = "#89dceb"
    accent_color = "#f28fad"
    accent_green_color = "#a1e56e"

    opened_script_cards = {}

    # Создание таблиц (если они не существуют)
    create_tables()

    # Список для хранения скриптов
    scripts = get_scripts()

    def get_script_row(script):
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(script.name, size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor="#313244",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e, script_for_card=script: show_script_card(e, script_for_card),
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.icons.PLAY_ARROW,
                    icon_color=accent_green_color,
                    on_click=lambda e, cmd=script.command: run_script_from_db(cmd),
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    icon_color=accent_color,
                    on_click=lambda e, script_id=script.id: delete_script(e, script_id),
                ),
            ],
            spacing=10,
        )

    def delete_script(e, script_id):
        deleted_script_name = delete_script_from_db(script_id)
        status_bar.value = f"Скрипт с ID {deleted_script_name} удален!"
        status_bar.color = accent_color
        page.update()

        update_scripts_container()  # Функция для обновления списка скриптов
        # Обновление списка скриптов после удаления

    def update_scripts_container():
        # Получаем обновленный список скриптов из базы данных
        scripts = get_scripts()

        # Очищаем текущий список скриптов в контейнере
        scripts_container.controls.clear()

        # Добавляем заново все скрипты
        for script in scripts:
            script_button = get_script_row(script)
            scripts_container.controls.append(script_button)

        # Обновление интерфейса после добавления элементов
        page.update()

    def show_script_card(e, script):
        if script.name in opened_script_cards:
            scripts_container.controls.remove(opened_script_cards[script.name])
            opened_script_cards.pop(script.name)
            page.update()
            return
        # Создаем карточку скрипта
        script_card = ft.Card(
            content=ft.Column(
                [
                    ft.Text(
                        script.name,
                        size=20,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        script.command,
                        size=16,
                        color=ft.colors.WHITE,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.PLAY_ARROW,
                                icon_color=accent_green_color,
                                on_click=lambda e, cmd=script.command: run_script_from_db(cmd),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=accent_color,
                                on_click=lambda e, script_id=script.id: delete_script(e, script_id),
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                spacing=10,
            ),
            variant=ft.CardVariant.ELEVATED,
        )

        for i in range(len(scripts_container.controls)):
            element = scripts_container.controls[i]
            if hasattr(element, "controls") and element.controls[0].content.value == script.name:
                script_index = i
                break
        else:
            raise ValueError(f"No element found for script name: {script.name}")
        scripts_container.controls.insert(script_index + 1, script_card)

        opened_script_cards[script.name] = script_card
        page.update()

    def add_script(e):
        if not input_name.value.strip() or not input_command.value.strip():
            status_bar.value = "Имя и команда не могут быть пустыми!"
            status_bar.color = accent_color
            page.update()
            return

        script_name = input_name.value.strip()
        command = input_command.value.strip()

        # Сохраняем скрипт в базе данных и получаем объект скрипта
        new_script = add_script_to_db(script_name, command)

        # Создание кнопки для выполнения команды
        def run_script(e, cmd=command, script_name=script_name):
            run_script_from_db(cmd)
            status_bar.value = f"Скрипт \"{script_name}\" выполнен!"
            status_bar.color = neon_color
            page.update()

        # Кнопка для нового скрипта
        script_button = ft.Row(
            [
                ft.Container(
                    content=ft.Text(script_name, size=16, color=ft.colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor="#313244",
                    padding=10,
                    border_radius=8,
                    on_click=lambda e, script=new_script: show_script_card(e, script),
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.icons.PLAY_ARROW,
                    icon_color=accent_green_color,
                    on_click=lambda e, cmd=new_script.command: run_script(cmd, script_name),
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    icon_color=accent_color,
                    on_click=lambda e: delete_script(e, new_script.id)
                ),
            ],
            spacing=10,
        )
        # Добавляем кнопку скрипта в интерфейс
        scripts_container.controls.append(script_button)

        # Очистка полей ввода
        input_name.value = ""
        input_command.value = ""

        # Обновление статуса
        status_bar.value = f"Скрипт \"{script_name}\" добавлен!"
        status_bar.color = neon_color
        page.update()

    # Ввод имени и команды
    input_name = ft.TextField(
        label="Имя скрипта",
        label_style=ft.TextStyle(color=neon_color),
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=neon_color,
        focused_border_color=accent_color,
        height=50,
    )
    input_command = ft.TextField(
        label="Команда для терминала",
        label_style=ft.TextStyle(color=neon_color),
        text_style=ft.TextStyle(color=ft.colors.WHITE),
        border_color=neon_color,
        focused_border_color=accent_color,
        height=50,
    )
    add_button = ft.ElevatedButton(
        text="Добавить",
        on_click=add_script,
        style=ft.ButtonStyle(
            bgcolor=neon_color,
            color=ft.colors.BLACK,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    # Панель со статусом
    status_bar = ft.Text(
        value="Добро пожаловать в ScriptHelper!",
        color=neon_color,
        size=14,
    )

    # Список скриптов
    scripts_container = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        controls=[
            get_script_row(script)
            for script in scripts
        ],
    )

    # Основная компоновка
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "ScriptHelper",
                        size=28,
                        color=neon_color,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(color=neon_color, thickness=1),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    input_name,
                                    input_command,
                                    add_button,
                                ],
                                spacing=15,
                                width=300,
                            ),
                            ft.Container(
                                content=scripts_container,
                                bgcolor="#24273a",
                                padding=10,
                                border_radius=10,
                                expand=True,
                                height=400,
                            ),
                        ],
                        spacing=20,
                    ),
                    ft.Divider(color=neon_color, thickness=1),
                    status_bar,
                ],
                spacing=20,
            ),
            padding=20,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)

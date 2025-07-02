from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.scrollview import ScrollView
import json
import os
from datetime import datetime
from functools import partial
import shutil
from pathlib import Path


class NodeSnap(MDApp):
    def build(self):
        self.notes_file = "notatki.json"
        self.notatki = self.wczytaj_notatki()
        self.sortuj_malejaco = True
        self.tryb_edycji = False
        self.edytowany_index = False
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.material_style = "M3"

        self.layoult = MDBoxLayout(orientation="vertical", padding=20, spacing=20)
        self.label = MDLabel(text="Witaj w NodeSnap!", halign="center", font_style="H5")
        
        self.sort_button = MDRaisedButton(
            text="Sortuj: najnowsze",
            pos_hint={"center_x": 0.5},
            on_release=self.toggle_sortowanie
        )

        self.tytul_input = MDTextField(hint_text="Tytuł notatki")
        self.tresc_input = MDTextField(hint_text="Treść notatki:", multiline=True, size_hint=(0.8, None), pos_hint={"center_x":0.5})

        self.przycisk = MDRaisedButton(
            text="Dodaj notatkę",
            pos_hint={"center_x": 0.5},
            on_release=self.dodaj_notatke
        )

        self.backup_btn = MDRaisedButton(
            text="Backup",
            pos_hint = {"center_x": 0.5},
            on_release = lambda x:self.backup_do_folderu()
        )
        self.entry = MDTextField(
            hint_text = "Tytuł notatki",
            helper_text = "To pole nie może być puste",
            helper_text_mode = "on_error",
            mode="rectangle",
            size_hint =(0.8, None),
            height=100,
            pos_hint={"center_x":0.5}
        )

        self.scroll_layoult = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.scroll_layoult.bind(minimum_height=self.scroll_layoult.setter("height"))

        self.scroll = ScrollView(size_hint=(1,1))
        self.scroll.add_widget(self.scroll_layoult)

        self.layoult.add_widget(self.label)
        self.layoult.add_widget(self.tytul_input)
        self.layoult.add_widget(self.tresc_input)
        self.layoult.add_widget(self.przycisk)
        self.layoult.add_widget(self.entry)
        self.layoult.add_widget(self.scroll)
        self.layoult.add_widget(self.sort_button)
        self.layoult.add_widget(self.backup_btn)

        return self.layoult
    
    def dodaj_notatke(self, instance):
        tytul = self.tytul_input.text
        tresc = self.tresc_input.text
        data = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not tytul or not tresc:
            self.label.text = "Uzupełnij wszystkie pola"
            return
        

        nowa_notatka = {
            "tytul" : tytul,
            "tresc" : tresc,
            "data" : data
        }

        if self.tryb_edycji and self.edytowany_index is not None:
            self.notatki[self.edytowany_index]["tytul"] = tytul
            self.notatki[self.edytowany_index]["tresc"] = tresc
            self.notatki[self.edytowany_index]["data"] = data
            self.label.text = f"Zaktualizowano notatkę"
        else:
            self.notatki.append(nowa_notatka)
            self.label.text=f"Zapisano notatkę{tytul}"

        self.tryb_edycji = False
        self.edytowany_index = None
        self.przycisk.text = "Dodaj notatkę"
        self.tytul_input.text = ""
        self.tresc_input.text = ""
        self.zapisz_notatke()
        self.wyswietl_notatki()

    def zapisz_notatke(self):
        with open(self.notes_file, "w", encoding="utf-8") as file:
            json.dump({"notatki" : self.notatki},file, ensure_ascii=False, indent=4)


    def wczytaj_notatki(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as file:
                    dane = json.load(file)
                    return dane.get("notatki", [])
            except Exception as e:
                print(f"Niepowodzenie:  {e}")
                return []
        return []

    def wyswietl_notatki(self):
        self.scroll_layoult.clear_widgets()
        
        notatki_do_wyswietlenia = self.notatki[::-1] if self.sortuj_malejaco else self.notatki
        for index, notatka in enumerate (notatki_do_wyswietlenia):
            card = MDCard(orientation="vertical", padding=10, size_hint=(1, None), height=120)

            tytul_rzad = MDBoxLayout(orientation="horizontal", spacing=10)

            tytul_label = MDLabel(
                text=f"[b]{notatka['tytul']}[/b]",
                markup=True,
                font_style="Subtitle1",
                theme_text_color="Primary"
            )

            kosz_btn = MDFlatButton(
                text="usun",
                on_release=partial(self.usun_notatke, len(self.notatki) - 1 - index),
                theme_text_color = "Custom",
                text_color=(1,0,0,1),
                pos_hint = {"center_y": 0.5}
            )

            pokaz_btn = MDFlatButton(
                text="Pokaż",
                on_release=partial(self.pokaz_tresc, notatka),
                theme_text_color = "Custom",
                text_color=(0,0.5,1,1),
                pos_hint = {"center_y": 0.5}
            )

            edytuj_btn = MDFlatButton(
                text="Edytuj",
                on_release=partial(self.zaladuj_do_edycji, len(self.notatki) - 1 - index),
                theme_text_color ="Custom",
                text_color = (1,0.5,0,1),
                pos_hint={"center_y": 0.5}
            )

            tytul_rzad.add_widget(tytul_label)
            tytul_rzad.add_widget(pokaz_btn)
            tytul_rzad.add_widget(kosz_btn)
            tytul_rzad.add_widget(edytuj_btn)

            data_label = MDLabel(
                text=f"[size=12][color=888888]{notatka['data']}[/color][/size]",
                markup=True,
                theme_text_color="Secondary"
            )

            card.add_widget(tytul_rzad)
            card.add_widget(data_label)

            self.scroll_layoult.add_widget(card)

    def zaladuj_do_edycji(self,index, *args):
        notatka = self.notatki[index]
        self.tytul_input.text = notatka["tytul"]
        self.tresc_input.text = notatka["tresc"]
        self.tryb_edycji = True
        self.edytowany_index = index
        self.przycisk.text = "Zapisz zmiany"
        self.label.text = f"Edytujesz notatkę: {notatka['tytul']}"

    def _klikniecie_karty(self, notatka, instance, touch):
        try:
            
            if instance.collide_point(*touch.pos) and not isinstance(touch.grab_current, MDIconButton):
                self.pokaz_tresc(notatka)
                return True
        except:
            pass
        return False

    def pokaz_tresc(self, notatka, *args):
        dialog = MDDialog(
            title=notatka["tytul"],
            text=notatka["tresc"],
            buttons=[MDFlatButton(text="zamknij", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def usun_notatke(self, index, *args):
        notatka = self.notatki[index]
        self.dialog_usun = MDDialog(
            title="Potwierdzenie usunięcia",
            text=f"Czy na pewno chcesz usunąć: [b]{notatka['tytul']}[/b]?",
            buttons=[
                MDFlatButton(
                    text="Anuluj",
                    on_release=lambda x:self.dialog_usun.dismiss()
                ),
                MDFlatButton(
                    text="Tak",
                    text_color =(1,0,0,1),
                    on_release=partial(self.potwierdz_usuniecie, index)
                )
            ]
        )
        self.dialog_usun.open()
        

    def potwierdz_usuniecie(self, index, *args):
        del self.notatki[index]
        self.zapisz_notatke()
        self.wyswietl_notatki()
        self.dialog_usun.dismiss()

    def toggle_sortowanie(self, *args):
        self.sortuj_malejaco = not self.sortuj_malejaco
        self.sort_button.text = "Sortuj: Najnowsze" if self.sortuj_malejaco else "Sortuj najstarsze"
        self.wyswietl_notatki()

    def backup_do_folderu(self):
        folder_backup = Path.home() / "NoteSnap_backup"
        folder_backup.mkdir(exist_ok=True)

        sciezka_backup = folder_backup / "notatki_backup.json"
        shutil.copy(self.notes_file, sciezka_backup)

        self.label.text = f"Backup zapisany w: {sciezka_backup}"


NodeSnap().run()
"""GUI smoke test; package with the same exclusions as the release build."""
import sys
from pathlib import Path

import carx_currency_editor as app


def main():
    app.self_test()
    window = app.EditorWindow()
    errors = []
    window.root.report_callback_exception = lambda *args: errors.append(args)
    try:
        if getattr(sys, 'frozen', False):
            resources = Path(sys._MEIPASS)
            assert Path(window.root.tk.eval('info library')) == resources / '_tcl_data'
            assert Path(window.root.tk.eval('set tk_library')) == resources / '_tk_data'
        window.root.update()
        for language, choice in (('en', 'English'), ('ru', 'Русский')):
            window.language_choice.set(choice)
            window.language_combo.event_generate('<<ComboboxSelected>>')
            window.root.update()
            assert window.language_code == language
            assert window.first_button.cget('text') == window.t('first_scan_button')
            window.root.tk.call('ttk::combobox::Post', str(window.language_combo))
            window.root.update()
            window.root.tk.call('ttk::combobox::Unpost', str(window.language_combo))
            window.cash_check.invoke()
            assert window.cash_current_entry.instate(['disabled'])
            window.cash_check.invoke()
            assert not window.cash_current_entry.instate(['disabled'])
            window.premium_check.invoke()
            assert window.premium_current_entry.instate(['disabled'])
            window.premium_check.invoke()
            window.cash_current_entry.delete(0, 'end')
            window.cash_current_entry.insert(0, '12345')
            window.premium_current_entry.delete(0, 'end')
            window.premium_current_entry.insert(0, '678')
            assert window.parse_selected(False, language, 'source') == {
                'cash': 12345.0, 'premium': 678.0,
            }
            # Exercise validation without connecting to the game or opening a modal.
            messages = []
            original_showerror = app.messagebox.showerror
            app.messagebox.showerror = lambda *args: messages.append(args)
            try:
                window.current_cash.set('invalid')
                window.first_button.invoke()
                assert len(messages) == 1
            finally:
                app.messagebox.showerror = original_showerror
            window.root.update()
        opened = []
        original_open = app.webbrowser.open
        app.webbrowser.open = lambda url, **kwargs: opened.append(url)
        try:
            window.open_donation()
            assert opened == [app.DONATION_URL]
        finally:
            app.webbrowser.open = original_open
        assert not errors, errors
    finally:
        window.root.destroy()
    print('Packaged GUI smoke test: OK (languages, dropdown, fields, checkboxes, validation, link callback)')


if __name__ == '__main__':
    main()

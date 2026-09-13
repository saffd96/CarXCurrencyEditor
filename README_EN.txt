CarX Currency Editor — offline CarX Street 1.8.0
=================================================

Purpose
-------
This program changes cash and premium currency in the running offline game.
It does not decrypt or replace an open save file. The game saves the new values
itself when you exit normally.

How to use
----------
1. Start offline CarX Street 1.8.0 and open a screen showing the required balance.
2. Start CarXCurrencyEditor_1.8.0.exe with a normal double-click. The app automatically
   requests administrator rights through UAC; confirm the Windows prompt.
3. The app automatically follows the Windows display language. Russian is used on
   Russian systems; English is the fallback for every other language. You can still
   switch languages in the upper-right corner of the window.
4. Select the currencies you want to change. You can leave all unselected fields
   empty.
5. Enter the exact current values of the selected currencies and click “First scan”.
6. After the scan finishes, spend or earn at least one selected currency in the game.
7. Enter the new current values in the same selected fields. Enter the target values
   on the right.
8. Click “Rescan and replace”.
9. Wait for the success message, check the balances in the game, and exit through
   the game menu.

If a currency is not found
--------------------------
- Check the current amounts you entered.
- Open a screen showing the required balances and restart from the first scan.
- Make sure at least one selected currency changes after the first scan.
- Do not change the selections between the first and second scans. To use a different
  selection, run the first scan again.
- Make sure you are using offline game version 1.8.0.

Important
---------
- Do not use this program in the networked or official online version.
- Balances use the float type. The game rounds 999,999,999 to 1,000,000,000.
- Memory scanning may take 10 to 60 seconds.
- Diagnostic log: %LOCALAPPDATA%\CarXCurrencyEditor\editor.log

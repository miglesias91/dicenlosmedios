& C:/Users/manuel/repos/dicenlosmedios/env/Scripts/activate.ps1

$ayer = (Get-Date).AddDays(-1).ToString("yyyyMMdd")

py C:/Users/manuel/repos/dicenlosmedios/dlm.py --top-terminos 50 --fecha $ayer --twittear
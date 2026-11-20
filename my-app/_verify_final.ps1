$ErrorActionPreference = "Stop"
$files = Get-ChildItem "C:\Users\david_ssemz9t\Downloads\*.docx" | Where-Object { $_.Name -like "*_COMPLETO.docx" }
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
foreach ($f in $files) {
    try {
        $doc = $word.Documents.Open($f.FullName, $false, $true)
        $pages = $doc.ComputeStatistics(2)
        $words = $doc.ComputeStatistics(0)
        $pdf = [System.IO.Path]::ChangeExtension($f.FullName, ".pdf")
        $doc.ExportAsFixedFormat($pdf, 17)
        Write-Output ("OK  | {0} | pages={1} | words={2}" -f $f.Name, $pages, $words)
        $doc.Close($false)
    } catch {
        Write-Output ("ERR | {0} | {1}" -f $f.Name, $_.Exception.Message)
    }
}
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null

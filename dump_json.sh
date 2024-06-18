# f="$1"

# # for f in logs/*/*/*.gpt-4-0125-preview.*.json ; 
# outdir=./$(dirname "$f") ; mkdir -p "$outdir" ; 
# outname="$(basename "$f")" ; 
# outname="${outname/.json/.html}"; echo "$f" ; 
# python ./llm_ctf/dump_commands.py "$f" | ansi2html -l -s osx | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "$outdir"/"$outname" ; 

for f in logs/*/*/*/*/*.json ; 
do outdir=./html/$(dirname "$f") ; 
mkdir -p "$outdir" ; outname="$(basename "$f")" ; 
outname="${outname/.json/.html}"; 
echo "$f" ; 
python ./llm_ctf/dump_commands.py "$f" | ansi2html -l -s osx | sed 's/color: #AAAAAA;/color: #FFFFFF;/g' > "$outdir"/"$outname" ; done
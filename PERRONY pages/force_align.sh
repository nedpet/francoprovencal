# takes the chapter texts in raw with the chapter audios in audios and force aligns them,
# outputting an eaf file in aligned_audios

if test $# -ne 2
then
    echo 'Usage: sh force_align.sh start_chapter end_chapter'
else
    for i in `seq $1 $2`
    do
        readalongs align -l fra -o eaf raw/chapter$i.txt audios/chapter$i.mp3 aligned_audios/chapter$i
    done
fi
while getopts ":y:e:t:c:" opt
do
    case $opt in
        y)
        year="$OPTARG"
        # echo $year
        ;;
        e)
        event="$OPTARG"
        # echo $event
        ;;
        t)
        category="$OPTARG"
        # echo $category
        ;;
        c)
        chal="$OPTARG"
        # echo $chal
        ;;
        ?)
        echo "usage: -y {year} -e {event} -t {category} -c {challenge}"
        exit 1;;
    esac
done


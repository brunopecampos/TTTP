mkdir ./tests/$2

for ((i = 0 ; i < 100 ; i++));
do 
  b=$(echo "scale=1; $i/2")
  c=$(echo $b | bc)
  (sleep "$c" && docker stats $1 --no-stream --format "{{.CPUPerc}}" >> ./tests/$2/$3 ) &
  (sleep "$c" && docker stats $1 --no-stream --format "{{.NetIO}}" >> ./tests/$2/$4 ) &
done
#sleep 30
sleep 5
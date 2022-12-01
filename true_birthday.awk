#!/usr/bin/env -S gawk -f

/Earth/{
	split($1, datearray, /-/)
	daybin[datearray[3]]+=1
	print
	for (day in daybin) {
		printf("%d: %d\n", day, daybin[day])
	}
}

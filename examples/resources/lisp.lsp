(fun add (x: List[number], y: number) (+ x y))

(fun range (start: number, end: number)
    (if (not (= start end))
        (++ (- end 1) (range start (- end 1)))
        (list)
    )
)

(fun randlist (n: number)
    (if (> n 0)
        (++ (int (* 100 (randval))) (randlist (- n 1)))
        (list)))

(fun tcorandlist (n: number, acc: number)
    (if (> n 0)
        (tcorandlist (- n 1) (++ (int (* 100 (randval))) acc))
        acc))

(fun quicksort (xs: list)
    (if xs
        (+
            (quicksort
                (filter
                    (lambda (x) (< x (first xs)))
                    (rest xs)))
            (list (first xs))
            (quicksort
                (filter
                    (lambda (x) (>= x (first xs)))
                    (rest xs))))
        (list))
)

(fun main ()
    (print (quicksort (tcorandlist 100 (list)))))
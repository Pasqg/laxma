(fun add (x y) (+ x y))

(fun quickSort (xs)
    (if xs
        (+
            (quickSort
                (filter
                    (lambda (x) (< x (first xs)))
                    (rest xs)))
            (list (first xs))
            (quickSort
                (filter
                    (lambda (x) (>= x (first xs)))
                    (rest xs))))
        (list))
)

(fun main ()
    (print (quickSort (list 5 5 5 3 99 33 -22 2 7 5 5 6 5 5 5 41 51 -7))))
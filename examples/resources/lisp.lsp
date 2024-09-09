(fun add (x y) (+ x y))

(fun main ()
    (print
        (map (lambda (x) (+ x 2))
            (append (list 11 41 45) 17 -5)))
    (print "Done"))
(fun add (x y) (+ x y))

(fun main ()
    (print
        (map (lambda (x) (if (or (= x 17) True) (* x 100) (* x -1)))
            (append (list 11 41 45) 17 5)))
    (print "Done"))
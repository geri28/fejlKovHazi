(deffacts init
	(jatekos 1)
	(jatekos 2)
	(jatekos 3)
	(jatekos 4)
	(jatekos 5)

	(nevek anna bence tamara gusztav vilmos)
    (varosok oroshaza eger nagykanizsa pecs sopron)
    (temakor popzene irodalom mitologia sport tortenelem)
    ;(helyezes elso masodik harmadik negyedik otodik)
)
(defrule print
  (solution
    anna ?ANNA
    bence ?BENCE
    gustav ?GUSTAV
    tamara ?TAMARA
    vilmos ?VILMOS

    popzene ?POPZENE
    irodalom ?IRODALOM
    mitologia ?MITOLOGIA
    sport ?SPORT
    tortenelem ?TORTENELEM

    eger ?EGER
    nagykanizsa ?NAGYKANIZSA
    oroshaza ?OROSHAZA
    pecs ?PECS
    sopron ?SOPRON
  )
  =>
  (printout t crlf "=== EREDMÉNYEK ===" crlf)
  (foreach ?nev (create$ anna bence gustav tamara vilmos)
    (bind ?hely (if (eq ?nev ?ANNA) then 1
               else (if (eq ?nev ?BENCE) then 2
               else (if (eq ?nev ?GUSTAV) then 3
               else (if (eq ?nev ?TAMARA) then 4
               else 5)))))
    
    (bind ?tema (if (eq ?nev ?POPZENE) then "Popzene"
               else (if (eq ?nev ?IRODALOM) then "Irodalom"
               else (if (eq ?nev ?MITOLOGIA) then "Mitológia"
               else (if (eq ?nev ?SPORT) then "Sport"
               else "Történelem")))))
    
    (bind ?varos (if (eq ?nev ?EGER) then "Eger"
               else (if (eq ?nev ?NAGYKANIZSA) then "Nagykanizsa"
               else (if (eq ?nev ?OROSHAZA) then "Orosháza"
               else (if (eq ?nev ?PECS) then "Pécs"
               else "Sopron")))))

    (printout t ?nev ": helyezés: " ?hely ", erősség: " ?tema ", város: " ?varos crlf)
  )
)

(defrule solve
; pecsi 4.
(jatekos ?PECS)
(jatekos ?PECS&4)
;Vilmos 2. lett
(jatekos ?VILMOS&2)
;(jatekos ?MASODIK&~?NEGYEDIK&?VILMOS)
;oroshazi HOLGY erossege popzene
(jatekos ?POPZENE)
(jatekos ?OROSHAZA&~?PECS&?POPZENE)
;Eger FIA gyengeje az irodalom
(jatekos ?IRODALOM&~?POPZENE)
(jatekos ?EGER&~?PECS&~?OROSHAZA&~?IRODALOM)
;Bence sportkerdesekhey ert
(jatekos ?BENCE&~?VILMOS)
(jatekos ?SPORT&~?POPZENE&~?IRODALOM&?BENCE)
;Gusztav nagykanizsai
(jatekos ?GUSZTAV&~?BENCE&~?VILMOS)
(jatekos ?NAGYKANIZSA&~?EGER&~?PECS&~?OROSHAZA&?GUSZTAV)
;Anna tovabb maradt jatekban mint bence, de hamarabb kiesett mint a tortenelem kerdesbol ugyes jatekos
(jatekos ?ANNA&~?GUSZTAV&~?BENCE&~?VILMOS)
(jatekos ?TORTENELEM&~?SPORT&~?POPZENE&~?IRODALOM&~?ANNA)
(test  (and (< ?ANNA ?BENCE)
            (< ?TORTENELEM ?BENCE)
            (> ?ANNA ?TORTENELEM)))
;elso helyezett nem Nagykanizsai es mitologia a jo neki
(jatekos ?MITOLOGIA&~?TORTENELEM&~?SPORT&~?POPZENE&~?IRODALOM&~?NAGYKANIZSA&1)
(jatekos ?TAMARA&~?ANNA&~?GUSZTAV&~?BENCE&~?VILMOS)
(jatekos ?SOPRON&~?NAGYKANIZSA&~?EGER&~?PECS&~?OROSHAZA)
(or(jatekos ?OROSHAZA&?ANNA) (jatekos ?OROSHAZA&?TAMARA))
(or(jatekos ?EGER&?BENCE) (jatekos ?EGER&?VILMOS) (jatekos ?EGER&?GUSZTAV))
=>
; 
(assert (solution
anna ?ANNA bence ?BENCE gusztav ?GUSZTAV tamara ?TAMARA vilmos ?VILMOS
popzene ?POPZENE irodalom ?IRODALOM mitologia ?MITOLOGIA sport ?SPORT tortenelem ?TORTENELEM
eger ?EGER nagykanizsa ?NAGYKANIZSA oroshaza ?OROSHAZA pecs ?PECS sopron ?SOPRON

))
)

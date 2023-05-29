PRAGMA temp_store = 2;

CREATE TEMP TABLE IF NOT EXISTS [temp]._Variables (
    countQuest  INTEGER,
    idUser      INTEGER,
    idIteration INTEGER
);

DELETE FROM [temp]._Variables;

/*Динамически изменяемая часть*/

INSERT INTO _Variables (
                           countQuest,
                           idUser,
                           idIteration
                       )
                       VALUES (
                           {0},
                           {1},
                           {2}
                       );

INSERT INTO temp_result_table (
                                  id_test,
                                  id_student,
                                  id_question
                              )
                              SELECT 
                                     {3},
                                     temp_all_variant.id_student,
                                     temp_all_variant.id_question
                                FROM temp_all_variant
                                     INNER JOIN
                                     [temp]._Variables AS _Variables ON temp_all_variant.id_student = _Variables.IdUser
                                     LEFT JOIN
                                     (
                                         SELECT id_question,
                                                count(id_student) 
                                           FROM temp_result_table
                                          GROUP BY id_question
                                         HAVING count(id_student) = (
                                                                    SELECT idIteration
                                                                      FROM [temp]._Variables
                                                                )
                                     )
                                     AS countQuest ON (temp_all_variant.id_question = countQuest.id_question)
                                     WHERE countQuest.id_question IS NULL
 /*                                    Questions where Questions.id_question = temp_all_variant.id_question*/
                               LIMIT (
                                         SELECT countQuest
                                           FROM [temp]._Variables
                                     ); 
SELECT count(*) FROM temp_result_table 
INNER JOIN 
[temp]._Variables AS _Variables ON temp_result_table.id_student = _Variables.IdUser;
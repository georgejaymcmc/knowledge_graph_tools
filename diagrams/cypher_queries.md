### File names and count that occur in more than one directory
```cypher
MATCH (d:Directory)-[:CONTAINS]->(f:FileName)
     -[:IS_TYPE_OF]->(ft:FileType)
WHERE ft.type = "Javascript"

WITH f.name AS file_name,
     collect(DISTINCT d.name) AS directories,
     count(DISTINCT d) AS directory_count

WHERE directory_count > 1

RETURN
    file_name,
    directory_count,
    directories

ORDER BY file_name
```
### For display in a Gradio dataframe or select box: one row per directory/file combination for File names that occur in more than one directory
```cypher
MATCH (d:Directory)-[:CONTAINS]->(f:FileName)-[:IS_TYPE_OF]->(ft:FileType)
WHERE ft.type = "Javascript"

WITH f.name AS file_name, count(DISTINCT d) AS directory_count
WHERE directory_count > 1

MATCH (d:Directory)-[:CONTAINS]->(f:FileName)
WHERE f.name = file_name

RETURN
    file_name,
    d.name AS directory
ORDER BY file_name, directory
```



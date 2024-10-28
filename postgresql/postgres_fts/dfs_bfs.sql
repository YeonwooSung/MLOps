-- basic dfs
WITH RECURSIVE search_tree(id, link, data, path) AS (
    SELECT t.id, t.link, t.data, ARRAY[t.id]
    FROM tree t
    UNION ALL
    SELECT t.id, t.link, t.data, path || t.id
    FROM tree t, search_tree st
    WHERE t.id = st.link
)
SELECT * FROM search_tree ORDER BY path;

-- dfs with search term
WITH RECURSIVE search_tree(id, link, data, path) AS (
    SELECT t.id, t.link, t.data, ARRAY[t.id]
    FROM tree t
    WHERE to_tsvector('english', t.data) @@ to_tsquery('english', 'your_search_term')
    UNION ALL
    SELECT t.id, t.link, t.data, path || t.id
    FROM tree t, search_tree st
    WHERE t.id = st.link 
    AND to_tsvector('english', t.data) @@ to_tsquery('english', 'your_search_term')
)
SELECT * FROM search_tree ORDER BY path;


-- basic bfs
WITH RECURSIVE search_tree(id, link, data, depth) AS (
    SELECT t.id, t.link, t.data, 0
    FROM tree t
  UNION ALL
    SELECT t.id, t.link, t.data, depth + 1
    FROM tree t, search_tree st
    WHERE t.id = st.link
)
SELECT * FROM search_tree ORDER BY depth;

-- bfs with search term
WITH RECURSIVE search_tree(id, link, data, depth) AS (
    SELECT t.id, t.link, t.data, 0
    FROM tree t
    WHERE to_tsvector('english', t.data) @@ to_tsquery('english', 'your_search_term')
  UNION ALL
    SELECT t.id, t.link, t.data, depth + 1
    FROM tree t, search_tree st
    WHERE t.id = st.link
      AND to_tsvector('english', t.data) @@ to_tsquery('english', 'your_search_term')
)
SELECT * FROM search_tree ORDER BY depth;

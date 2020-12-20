
# Tracking votes on content

Trying to track the number on votes on the content can be tricky.
Here is a naive way to track votes and a proposed solution.

|post_id|post_content|score|
|:------|:-----------|----:|
|1      |'hello'     |3    |

When a user votes we increment or decrement the score counter based upon
our user either upvoting(+1) or downvoting(-1).

Imagine our user _Steve_ wants to cast a vote, how are we going to verify
that _Steve_ hasn't already voted? The solution to this is to track for
which posts _Steve_ already has voted.

Ideally however we do not separately track all the votes and the scores 
we are simply able to calculate the score by summing all the votes.

|post_id|post_content|
|:------|:-----------|
|1      |hello       |
|2      |Goodbye     |

Our voting table.

|post_id|username|rating|
|:------|:-------|-----:|
|1      |Steve   |     1|
|1      |Bert    |    -1|
|1      |Rob     |     1|
|1      |Olaf    |     1|

Then when we need to retrieve the score we SUM the rating to get our 
total score.

```sql
SELECT post_id, SUM(rating) as 'score'
FROM votes
GROUP BY post_id
```

## Retrieving the top 5 posts


Imagine we want to retrieve the top 5 posts. A naive way of doing this 
might be to write the following query.

```sql
SELECT posts.post_id, SUM(votes.rating)  as 'score'
FROM posts
JOIN votes on posts.post_id = votes.post_id
GROUP BY posts.post_id
ORDER BY score DESC
LIMIT 5
```

This however will not include posts that have not received any votes yet.

|post_id|score|
|:------|----:|
|1      |    2|

A `JOIN` is an `INNER JOIN` by default, this means you'll only get 
entries when something is found both in the `votes` table and in the 
`posts` table. Here the fix is to create a `LEFT JOIN`.

This will also return the posts that did not receive any rating.

|post_id|score|
|:------|----:|
|1      |    2|
|2      | NULL|

This is already workable. Yet I prefer not having to deal with the
_NULL_ values in my Python code, hence I will ask to return 0 whenever 
_NULL_ manifests. This can be achieved with the following code.

```sql
CASE WHEN votes.rating IS NULL THEN 0 ELSE votes.rating 
```

This is the equivalent of an `if` statement. 
Our full query as found in the `get_top_posts`-function.

```sql
SELECT posts.post_id, SUM(
	CASE WHEN votes.rating IS NULL 
		THEN 0 
		ELSE votes.rating 
	END) as 'score'
FROM posts
LEFT JOIN votes on posts.post_id = votes.post_id
GROUP BY posts.post_id
ORDER BY score DESC
LIMIT 5
```

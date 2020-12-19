BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "posts" (
	"post_id"	INTEGER,
	"post_content"	TEXT,
	PRIMARY KEY("post_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "votes" (
	"post_id"	INTEGER NOT NULL,
	"username"	INTEGER NOT NULL,
	"rating"	TEXT NOT NULL,
	PRIMARY KEY("post_id","username")
);
INSERT INTO "posts" ("post_id","post_content") VALUES (1,'test'),
 (2,'a post');
INSERT INTO "votes" ("post_id","username","rating") VALUES (2,'Robbe','good');
COMMIT;

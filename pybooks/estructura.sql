--- DB structure

DROP TABLE IF EXISTS "books";
DROP SEQUENCE IF EXISTS books_id_seq;
CREATE SEQUENCE books_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."books" (
    "id" integer DEFAULT nextval('books_id_seq') NOT NULL,
    "isbn" character varying NOT NULL,
    "title" character varying NOT NULL,
    "author" character varying NOT NULL,
    "year" smallint NOT NULL,
    CONSTRAINT "books_pkey" PRIMARY KEY ("id")
) WITH (oids = false);

DROP TABLE IF EXISTS "reviews";
DROP SEQUENCE IF EXISTS reviews_id_seq;
CREATE SEQUENCE reviews_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."reviews" (
    "id" integer DEFAULT nextval('reviews_id_seq') NOT NULL,
    "score" smallint,
    "review" character varying,
    "created" timestamp NOT NULL,
    "book_id" integer NOT NULL,
    "user_id" integer NOT NULL,
    CONSTRAINT "reviews_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "reviews_book_id_fkey" FOREIGN KEY (book_id) REFERENCES books(id) NOT DEFERRABLE,
    CONSTRAINT "reviews_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(id) NOT DEFERRABLE
) WITH (oids = false);

DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_id_seq;
CREATE SEQUENCE users_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "id" integer DEFAULT nextval('users_id_seq') NOT NULL,
    "username" character varying NOT NULL,
    "name" character varying NOT NULL,
    "surname" character varying NOT NULL,
    "email" character varying NOT NULL,
    "created" timestamp NOT NULL,
    "passwd" character varying(128),
    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
) WITH (oids = false);
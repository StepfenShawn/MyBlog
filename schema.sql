drop database if exists awesome;
create database awesome;
use awesome;

grant select, insert, update, delete on awesome.* to 'root'@'localhost';

create table users (
  `id` varchar(50) not null,
  `email` varchar(50) not null,
  `passwd` varchar(50) not null,
  `admin` bool not null,
  `name` varchar(50) not null,
  `image` varchar(500) not null,
  `created_at` real not null,
  `location` varchar(50),
  unique key `idx_email` (`email`),
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

create table person_bookmark (
  `user_id` varchar(50) not null,
  `blog_id` varchar(50) not null,
  primary key (`user_id`)
) engine=innodb default charset=utf8;

create table person_follows (
  `user_id` varchar(50) not null,
  `follows_id` varchar(50) not null,
  primary key (`user_id`)
) engine=innodb default charset=utf8;

create table person_photoes (
  `user_id` varchar(50) not null,
  `image` mediumblob not null,
  primary key (`user_id`)
) engine=innodb default charset=utf8;

create table person_followers (
  `user_id` varchar(50) not null,
  `followers_id` varchar(50) not null,
  primary key (`user_id`)
) engine=innodb default charset=utf8;

create table blogs (
  `id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `user_name` varchar(50) not null,
  `user_image` varchar(500) not null,
  `name` varchar(50) not null,
  `summary` varchar(200) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  `vistors` integer not null default 0,
  `likes` integer not null default 0,
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
  `id` varchar(50) not null,
  `blog_id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `user_name` varchar(50) not null,
  `user_image` varchar(500) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  `likes` integer,
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

create table replies (
  `comment_id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `user_name` varchar(50) not null,
  `user_image` varchar(500) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  `likes` integer not null default 0,
  primary key (`comment_id`)
) engine=innodb default charset=utf8;

create table website (
  `id` varchar(50) not null,
  `vistors` integer not null default 0,
  primary key (`id`)
) engine=innodb default charset=utf8;
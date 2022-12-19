drop database if exists awesome;
create database awesome;
use awesome;

grant select, insert, update, delete on 'root'@'localhost' identified by 'root';

--创建用户表
create table users (
  `id` varchar(50) not null, --用户id
  `email` varchar(50) not null, --用户邮件
  `passwd` varchar(50) not null, --用户密码
  `admin` bool not null, --用户身份
  `name` varchar(50) not null, --用户名
  `image` varchar(500) not null, --头像
  `created_at` real not null, --注册时间
  unique key `idx_email` (`email`),
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

--创建博客表
create table blogs (
  `id` varchar(50) not null, --博客id
  `user_id` varchar(50) not null, --用户id
  `user_name` varchar(50) not null, --用户名
  `user_image` varchar(500) not null, --用户头像
  `name` varchar(50) not null, --标题
  `summary` varchar(200) not null, --专栏
  `content` mediumtext not null, --内容
  `created_at` real not null, --创建时间
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

--创建评论表
create table comments (
  `id` varchar(50) not null, -- 评论id
  `blog_id` varchar(50) not null, --博客id
  `user_id` varchar(50) not null, --用户id
  `user_name` varchar(50) not null, --用户名
  `user_image` varchar(500) not null, --用户头像
  `content` mediumtext not null, --评论内容
  `created_at` real not null, --评论时间
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;
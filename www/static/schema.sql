# 如果存在该用户，则删除
drop user 'www-data'@'%';
# 创建新用户
create user 'www-data'@'%' identified by 'www-data';
#创建数据库
drop database if exists awesome;
create database awesome;
use awesome;
# 给新用户赋值
grant select, insert, update, create on awesome.* to 'www-data'@'localhost';

create table users (
	# <字段名> <数据类型> NOT NULL设置非空约束
	`id` varchar(50) not null,
	`email` varchar(50) not null,
	`password` varchar(50) not null,
	`admin` varchar(50) not null,
	`name` varchar(50) not null,
	`image` varchar(500) not null,
	`created_at` real not null,
	# 定义字段每个值都唯一
	unique key `idx_email` (`email`),
	# 定义索引
	key `idx_created_at` (`created_at`),
	# 定义主键
	primary key(`id`)
) engine=innodb default charset=utf8;

create table blogs (
	`id` varchar(50) not null,
	`user_id` varchar(50) not null,
	`user_name` varchar(50) not null,
	`user_image` varchar(500) not null,
	`summary` varchar(200) not null,
	# 中长文本
	`content` mediumtext not null,
	`created_at` real not null,
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
	key `idx_created_at` (`created_at`),
	primary key (`id`)
) engine=innodb default charset=utf8;
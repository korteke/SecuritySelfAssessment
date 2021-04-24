create database if not exists ssa;
use ssa;
create table if not exists entries (id integer auto_increment primary key, submitter text, project text, date int, entries text, score text, business_unit text, formid text not null, company text not null);
create table if not exists companies (company nvarchar(256) primary key);
insert into companies (company) values('sample company');

grant all privileges on ssa.* to 'ssa'@'%' identified by 'ssapass1!!!1one';

drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);
drop table if exists parameters;
create table parameters (
    id integer primary key autoincrement,
    parameter_1 text not null,
    parameter_2 text not null
);

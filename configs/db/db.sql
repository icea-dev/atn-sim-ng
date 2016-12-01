CREATE DATABASE IF NOT EXISTS atn_sim;
grant all privileges on atn_sim.* to atn_sim@'%' identified by 'atn_sim';
use atn_sim
source atn_sim.sql

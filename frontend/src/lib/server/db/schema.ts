import { integer, pgTable, serial, text, varchar } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  fullName: text('full_name'),
  phone: varchar('phone', { length: 256 }),
});

export const orders = pgTable('orders', {
  id: serial('id').primaryKey(),
  userId: text('user_id'),
  instrument: text('instrument'),
  quantity: integer('quantity'),
  price: integer('price'),
  state: text('state'),
});
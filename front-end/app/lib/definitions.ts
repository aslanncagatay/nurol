// This file contains type definitions for your data.
// It describes the shape of the data, and what data type each property should accept.
// For simplicity of teaching, we're manually defining these types.
// However, these types are generated automatically if you're using an ORM such as Prisma.

export type Employee = {
  id: number;
  departmentId: number;
  name: string;
  age: number;
  position: string;
};

export type Department = {
  id: number;
  name: string;
  phone: number;
  location: string;
  budget: number;
  employees?: Employee[];
};

export type RabbitMessage = {
  messageId: string;
  message: string;
  messageDate: Date;
};

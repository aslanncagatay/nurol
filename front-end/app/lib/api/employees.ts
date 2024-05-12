"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { Employee } from "../definitions";

const FormSchema = z.object({
  id: z.coerce.number().min(1),
  departmentId: z.coerce.number().min(1),
  name: z.string().min(1),
  age: z.coerce.number().min(1),
  position: z.string().min(1),
});

const CreateEmployee = FormSchema;

// This is temporary
export type State = {
  errors?: {
    id?: string[];
    departmentId?: string[];
    name?: string[];
    age?: string[];
    position?: string[];
  };
  message?: string | null;
};

export async function createEmployee(prevState: State, formData: FormData) {
  // Validate form fields using Zod
  const validatedFields = CreateEmployee.safeParse({
    id: formData.get("employeeId"),
    departmentId: formData.get("departmentId"),
    name: formData.get("name"),
    age: formData.get("age"),
    position: formData.get("position"),
  });

  // If form validation fails, return errors early. Otherwise, continue.
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Missing fields. Failed to create employee.",
    };
  }

  // Prepare data for insertion into the database
  const { id, departmentId, name, age, position } = validatedFields.data;

  try {
    // Call addEmployee endpoint
    const response = await fetch("http://api-gateway-svc:80/employee", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, departmentId, name, age, position }),
    });

    // Check if the request was successful
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const newEmployee: Employee = await response.json();

    // Handle the response data as needed
    console.log("New Employee:", newEmployee);

    return {
      message: "Employee added successfully",
    };
  } catch (error) {
    // Handle any errors that occurred during Employee creation
    console.error("Error creating Employee:", error);
  } finally {
    // Revalidate the cache for the invoices page and redirect the user.
    revalidatePath("/employees");
    redirect("/employees");
  }
}

export async function getEmployees(): Promise<Employee[]> {
  try {
    // Call addEmployee endpoint
    const response = await fetch("http://api-gateway-svc:80/employee", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Check if the request was successful
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const employees: Employee[] = await response.json();

    // Handle the response data as needed
    console.log("Employees:", employees);

    return employees;
  } catch (error) {
    // Handle any errors that occurred during Employee creation
    console.error("Error creating Employee:", error);

    return [];
  }
}

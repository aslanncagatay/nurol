"use server";

import { z } from "zod";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { Department } from "../definitions";

const FormSchema = z.object({
  id: z.coerce.number().min(1),
  name: z.string().min(1),
  phone: z.coerce.number().min(1),
  location: z.string().min(1),
  budget: z.coerce.number().min(1),
});

const CreateDepartment = FormSchema;

// This is temporary
export type State = {
  errors?: {
    id?: string[];
    name?: string[];
    phone?: string[];
    location?: string[];
    budget?: string[];
  };
  message?: string | null;
};

export async function createDepartment(prevState: State, formData: FormData) {
  // Validate form fields using Zod
  const validatedFields = CreateDepartment.safeParse({
    id: formData.get("departmentId"),
    name: formData.get("name"),
    phone: formData.get("phone"),
    location: formData.get("location"),
    budget: formData.get("budget"),
  });

  // If form validation fails, return errors early. Otherwise, continue.
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Missing fields. Failed to create deparment.",
    };
  }

  // Prepare data for insertion into the database
  const { id, name, phone, location, budget } = validatedFields.data;

  try {
    // Call addDepartment endpoint
    const response = await fetch("http://af2ac53b90620498aa95b5ca5c35c9c6-694563710.eu-north-1.elb.amazonaws.com/department", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, name, phone, location, budget }),
    });

    // Check if the request was successful
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const newDepartment: Department = await response.json();

    // Handle the response data as needed
    console.log("New department:", newDepartment);

    return {
      message: "Department added successfully",
    };
  } catch (error) {
    // Handle any errors that occurred during department creation
    console.error("Error creating department:", error);
  } finally {
    // Revalidate the cache for the invoices page and redirect the user.
    revalidatePath("/departments");
    redirect("/departments");
  }
}

export async function getDepartments(): Promise<Department[]> {
  try {
    // Call addDepartment endpoint
    const response = await fetch("http://af2ac53b90620498aa95b5ca5c35c9c6-694563710.eu-north-1.elb.amazonaws.com/department", {
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
    const departments: Department[] = await response.json();

    // Handle the response data as needed
    console.log("Departments:", departments);

    return departments;
  } catch (error) {
    // Handle any errors that occurred during department creation
    console.error("Error creating department:", error);

    return [];
  }
}

export async function getDepartmentWithEmployees(
  departmentId: string,
): Promise<Department | null> {
  try {
    // Call addDepartment endpoint
    const response = await fetch(
      `http://af2ac53b90620498aa95b5ca5c35c9c6-694563710.eu-north-1.elb.amazonaws.com/department/with-employees/${departmentId}`,
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      },
    );

    // Check if the request was successful
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const department: Department = await response.json();

    // Handle the response data as needed
    console.log("Department:", department);

    return department;
  } catch (error) {
    // Handle any errors that occurred during department creation
    console.error("Error creating department:", error);

    return null;
  }
}

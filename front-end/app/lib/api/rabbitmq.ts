"use server";

import { z } from "zod";
import { RabbitMessage } from "../definitions";

const FormSchema = z.object({
  messageId: z.string().min(1),
  rabbitMessage: z.string().min(1),
  messageDate: z.coerce.date(),
});

const CreateMessage = FormSchema;

// This is temporary
export type State = {
  errors?: {
    messageId?: string[];
    rabbitMessage?: string[];
    messageDate?: string[];
  };
  message?: string | null;
};

export async function sendMessage(prevState: State, formData: FormData) {
  // Validate form fields using Zod
  const validatedFields = CreateMessage.safeParse({
    messageId: formData.get("messageId"),
    rabbitMessage: formData.get("rabbitMessage"),
    messageDate: formData.get("messageDate"),
  });
  console.log(validatedFields.data);
  // If form validation fails, return errors early. Otherwise, continue.
  if (!validatedFields.success) {
    return {
      errors: validatedFields.error.flatten().fieldErrors,
      message: "Missing fields. Failed to create deparment.",
    };
  }

  // Prepare data for insertion into the database
  const { messageId, rabbitMessage, messageDate } = validatedFields.data;

  try {
    // Call addDepartment endpoint
    const response = await fetch("http://api-gateway-svc:80/rabbitmq/send", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messageId, message: rabbitMessage, messageDate }),
    });

    // Check if the request was successful
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }

    // Parse the response as JSON
    const message: RabbitMessage = await response.json();

    // Handle the response data as needed
    console.log("New message:", message);

    return {
      message: "Message sent successfully",
    };
  } catch (error) {
    // Handle any errors that occurred during department creation
    console.error("Error sending rabbit message:", error);

    return {
      message: "Message could not send",
    };
  }
}

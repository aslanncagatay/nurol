"use client";

import Link from "next/link";
import { Button } from "@/app/ui/button";
import { sendMessage } from "@/app/lib/api/rabbitmq";
import { useFormState } from "react-dom";

export default function Form() {
  const initialState = { message: null, errors: {} };
  const [state, dispatch] = useFormState(sendMessage, initialState);

  return (
    <form action={dispatch}>
      <div aria-live="polite" aria-atomic="true">
        {state.message ? (
          <p className="mt-2 text-sm text-red-500">{state.message}</p>
        ) : null}
      </div>
      <div className="rounded-md bg-gray-50 p-4 md:p-6">
        {/* Message ID */}
        <div className="mb-4">
          <label
            htmlFor="departmentId"
            className="mb-2 block text-sm font-medium"
          >
            Message ID
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="messageId"
                name="messageId"
                type="number"
                step={0.01}
                placeholder="message ID"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
                aria-describedby="messageId-error"
              />
            </div>
          </div>

          <div id="messageId-error" aria-live="polite" aria-atomic="true">
            {state.errors?.messageId &&
              state.errors.messageId.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Message */}
        <div className="mb-4">
          <label
            htmlFor="rabbitMessage"
            className="mb-2 block text-sm font-medium"
          >
            Message
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="rabbitMessage"
                name="rabbitMessage"
                type="text"
                placeholder="enter your message"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
                aria-describedby="rabbitMessage-error"
              />
            </div>
          </div>

          <div id="rabbitMessage-error" aria-live="polite" aria-atomic="true">
            {state.errors?.rabbitMessage &&
              state.errors.rabbitMessage.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>

        {/* Message Date */}
        <div className="mb-4">
          <label
            htmlFor="messageDate"
            className="mb-2 block text-sm font-medium"
          >
            Message Date
          </label>
          <div className="relative mt-2 rounded-md">
            <div className="relative">
              <input
                id="messageDate"
                name="messageDate"
                type="date"
                placeholder="date"
                className="peer block w-full rounded-md border border-gray-200 py-2 pl-4 text-sm outline-2 placeholder:text-gray-500"
                aria-describedby="messageDate-error"
              />
            </div>
          </div>

          <div id="messageDate-error" aria-live="polite" aria-atomic="true">
            {state.errors?.messageDate &&
              state.errors.messageDate.map((error: string) => (
                <p className="mt-2 text-sm text-red-500" key={error}>
                  {error}
                </p>
              ))}
          </div>
        </div>
      </div>
      <div className="mt-6 flex justify-end gap-4">
        <Link
          href="/departments"
          className="flex h-10 items-center rounded-lg bg-gray-100 px-4 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-200"
        >
          Cancel
        </Link>
        <Button type="submit">Send Message</Button>
      </div>
    </form>
  );
}

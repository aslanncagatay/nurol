import Form from "@/app/ui/employees/create-form";
import Breadcrumbs from "@/app/ui/departments/breadcrumbs";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Create Employee",
};

export default async function Page() {
  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: "Employees", href: "/employees" },
          {
            label: "Create Employee",
            href: "/employees/create",
            active: true,
          },
        ]}
      />
      <Form customers={[]} />
    </main>
  );
}

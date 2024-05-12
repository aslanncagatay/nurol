import Form from "@/app/ui/departments/create-form";
import Breadcrumbs from "@/app/ui/departments/breadcrumbs";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Create Department",
};

export default async function Page() {
  return (
    <main>
      <Breadcrumbs
        breadcrumbs={[
          { label: "Departments", href: "/departments" },
          {
            label: "Create Department",
            href: "/departments/create",
            active: true,
          },
        ]}
      />
      <Form />
    </main>
  );
}

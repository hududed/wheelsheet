import { renderSnippet } from "$lib/components/ui/data-table/index.js";
import type { ColumnDef } from "@tanstack/table-core";
import { createRawSnippet } from "svelte";

// Define the Order type
export type Order = {
  created_at: Date;
  account_number: number;
  chain_symbol: string;
  expiration_date: Date;
  strike_price: number;
  net_amount: number;
  net_amount_direction: string;
  quantity: number;
  state: string;
};

// Define the columns
export const columns: ColumnDef<Order>[] = [
  {
    accessorKey: "created_at",
    header: "Created At",
    cell: ({ row }) => {
      const date = new Date(row.getValue("created_at"));
      return date.toLocaleString();
    },
  },
  {
    accessorKey: "account_number",
    header: "Account Number",
  },
  {
    accessorKey: "chain_symbol",
    header: "Chain Symbol",
  },
  {
    accessorKey: "expiration_date",
    header: "Expiration Date",
    cell: ({ row }) => {
      const date = new Date(row.getValue("expiration_date"));
      return date.toLocaleDateString();
    },
  },
  {
    accessorKey: "strike_price",
    header: () => {
      const strikePriceHeaderSnippet = createRawSnippet(() => ({
        render: () => `<div class="text-right">Strike Price</div>`,
      }));
      return renderSnippet(strikePriceHeaderSnippet, "");
    },
    cell: ({ row }) => {
      const strikePrice = row.getValue("strike_price");
      const strikePriceCellSnippet = createRawSnippet<[string]>((getStrikePrice) => {
        const strikePrice = getStrikePrice();
        return {
          render: () => `<div class="text-right font-medium">${strikePrice}</div>`,
        };
      });

      return renderSnippet(
        strikePriceCellSnippet,
        typeof strikePrice === "number" ? strikePrice.toFixed(2) : "N/A"
      );
    },
  },
  {
    accessorKey: "net_amount",
    header: () => {
      const netAmountHeaderSnippet = createRawSnippet(() => ({
        render: () => `<div class="text-right">Net Amount</div>`,
      }));
      return renderSnippet(netAmountHeaderSnippet, "");
    },
    cell: ({ row }) => {
      const netAmount = row.getValue("net_amount");
      const formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      });

      const netAmountCellSnippet = createRawSnippet<[string]>((getNetAmount) => {
        const netAmount = getNetAmount();
        return {
          render: () => `<div class="text-right font-medium">${netAmount}</div>`,
        };
      });

      return renderSnippet(
        netAmountCellSnippet,
        typeof netAmount === "number" ? formatter.format(netAmount) : "N/A"
      );
    },
  },
  {
    accessorKey: "net_amount_direction",
    header: "Net Amount Direction",
  },
  {
    accessorKey: "quantity",
    header: "Quantity",
  },
  {
    accessorKey: "state",
    header: "State",
  },
];
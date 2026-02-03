import * as React from "react";
import { Check, ChevronsUpDown, Plus } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

import { useGetFoldersQuery, useCreateFolderMutation } from "@/api/folder.api";

type Props = {
  value?: string;
  onChange: (value?: string) => void;
  disabledIds?: Set<string>;
};

export function FolderCombobox({ value, onChange, disabledIds }: Props) {
  const { data: folders = [] } = useGetFoldersQuery();
  const [createFolder] = useCreateFolderMutation();

  const [open, setOpen] = React.useState(false);
  const [input, setInput] = React.useState("");

  const selected = folders.find((f) => f.id === value);

  const handleCreate = async () => {
    if (!input.trim()) return;
    const folder = await createFolder({ name: input }).unwrap();
    onChange(folder.id);
    setInput("");
    setOpen(false);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          className="w-full justify-between"
        >
          {selected ? selected.name : "No folder"}
          <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50" />
        </Button>
      </PopoverTrigger>

      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput
            placeholder="Search or create folder…"
            value={input}
            onValueChange={setInput}
          />

          <CommandEmpty>
            <Button
              variant="ghost"
              className="w-full justify-start gap-2"
              onClick={handleCreate}
            >
              <Plus className="h-4 w-4" />
              Create “{input}”
            </Button>
          </CommandEmpty>

          <CommandGroup>
            <CommandItem onSelect={() => onChange(undefined)}>
              <Check
                className={cn(
                  "mr-2 h-4 w-4",
                  !value ? "opacity-100" : "opacity-0",
                )}
              />
              No folder
            </CommandItem>

            {folders.map((folder) => {
              const disabled = disabledIds?.has(folder.id);

              return (
                <CommandItem
                  key={folder.id}
                  disabled={disabled}
                  onSelect={() => {
                    if (disabled) return;
                    onChange(folder.id);
                    setOpen(false);
                  }}
                >
                  {folder.name}
                </CommandItem>
              );
            })}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
}

import * as React from "react";
import { Check, ChevronsUpDown, Plus, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
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

import { useGetTagsQuery, useCreateTagMutation } from "@/api/tag.api";

type Props = {
  value: string[];
  onChange: (value: string[]) => void;
};

export function TagsInput({ value, onChange }: Props) {
  const { data: tags = [] } = useGetTagsQuery();
  const [createTag] = useCreateTagMutation();

  const [open, setOpen] = React.useState(false);
  const [input, setInput] = React.useState("");

  const selectedTags = tags.filter((t) => value.includes(t.id));
  const availableTags = tags.filter((t) => !value.includes(t.id));

  const handleCreate = async () => {
    if (!input.trim()) return;

    // console.log("CREATING TAG:", input.trim());

    const tag = await createTag({ name: input.trim() }).unwrap();

    if (!value.includes(tag.id)) {
      onChange([...value, tag.id]);
    }

    setInput("");
    setOpen(false);
  };

  const toggleTag = (id: string) => {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  };

  return (
    <div className="space-y-2">
      {/* Selected tags */}
      <div className="flex flex-wrap gap-2">
        {selectedTags.map((tag) => (
          <Badge key={tag.id} variant="secondary">
            {tag.name}
            <button
              type="button"
              onClick={() => toggleTag(tag.id)}
              className="ml-1"
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
      </div>

      {/* Combobox-style dropdown (same as folders) */}
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            className="w-full justify-between"
          >
            Add tags
            <ChevronsUpDown className="ml-2 h-4 w-4 opacity-50" />
          </Button>
        </PopoverTrigger>

        <PopoverContent className="w-full p-0">
          <Command>
            <CommandInput
              placeholder="Search or create tag…"
              value={input}
              onValueChange={setInput}
            />

            <CommandEmpty>
              {input.trim().length > 0 && (
                <Button
                  variant="ghost"
                  className="w-full justify-start gap-2"
                  onClick={handleCreate}
                >
                  <Plus className="h-4 w-4" />
                  Create “{input}”
                </Button>
              )}
            </CommandEmpty>

            <CommandGroup>
              {availableTags.map((tag) => (
                <CommandItem
                  key={tag.id}
                  value={tag.name}
                  onSelect={() => {
                    toggleTag(tag.id);
                    setOpen(false);
                  }}
                >
                  <Check className={cn("mr-2 h-4 w-4 opacity-0")} />
                  {tag.name}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverContent>
      </Popover>
    </div>
  );
}

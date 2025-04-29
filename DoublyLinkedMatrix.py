class Node:
    def __init__(self, row=None, col=None):
        self.left = self
        self.right = self
        self.up = self
        self.down = self
        self.col = col # pointer to the column header
        self.row = row # row identifier
        self.x = None
        self.y = None


class ColumnNode(Node):
    def __init__(self, name):
        super().__init__(row=None, col=self)
        self.name = name
        self.size = 0
        self.up = self
        self.down = self

class DoublyLinkedMatrix:
    def __init__(self, matrix):
        self.header = ColumnNode("header")
        self.header.x = -1
        self.header.y = -1
        self.cols = []
        self.nodes = []
        self.current_column = None
        self.current_row = None
        self.current_solution = []

        self.build(matrix)

    def build(self, matrix):
        cols = len(matrix[0])
        # create column headers
        last = self.header

        for i in range(cols):
            col_node = ColumnNode(i)
            col_node.x = i  # column index
            col_node.y = -1  # header row above data rows
            self.nodes.append(col_node)
            self.cols.append(col_node)

            # link horizontally
            col_node.left = last
            col_node.right = self.header
            last.right = col_node
            self.header.left = col_node
            last = col_node

        # Create data nodes
        for r, row in enumerate(matrix):
            prev = None
            for c, val in enumerate(row):
                if val == 1:
                    col_node = self.cols[c]
                    new_node = Node(row=r, col=col_node)
                    new_node.x = c
                    new_node.y = r
                    self.nodes.append(new_node)

                    # link vertically
                    new_node.down = col_node
                    new_node.up = col_node.up
                    col_node.up.down = new_node
                    col_node.up = new_node

                    col_node.size += 1

                    # link horizontally within row
                    if prev:
                        new_node.left = prev
                        new_node.right = prev.right
                        prev.right.left = new_node
                        prev.right = new_node
                    else:
                        new_node.left = new_node
                        new_node.right = new_node

                    prev = new_node

    def print_columns(self):
        node = self.header.right
        while node != self.header:
            print(f"Column {node.name}: {node.size} entries")
            node = node.right

    def cover(self, col_node):
        self.on_cover(col_node)
        # Remove column header
        col_node.right.left = col_node.left
        col_node.left.right = col_node.right

        # For each node down the column
        i = col_node.down
        while i != col_node:
            # For each node right in the row
            j = i.right
            while j != i:
                j.down.up = j.up
                j.up.down = j.down
                j.col.size -= 1
                j = j.right
            i = i.down

    def uncover(self, col_node):
        self.on_uncover(col_node)
        # For each node up the column
        i = col_node.up
        while i != col_node:
            # For each node left in the row
            j = i.left
            while j != i:
                j.col.size += 1
                j.down.up = j
                j.up.down = j
                j = j.left
            i = i.up

        # Restore column header
        col_node.right.left = col_node
        col_node.left.right = col_node

    def search(self, solution=None, step_mode=False):
        if solution is None:
            solution = []
        self.current_solution = list(solution)

        if self.header.right == self.header:
            print("Solution:", solution)
            self.current_solution = list(solution)
            yield  # Yield back to Pygame runner
            return

        c = self.select_column()
        self.on_pick_column(c)
        self.cover(c)
        if step_mode:
            self.current_solution = list(solution)
            yield

        r = c.down
        while r != c:
            solution.append(r.row)
            self.on_pick_row(r)
            if step_mode:
                self.current_solution = list(solution)
                yield

            j = r.right
            while j != r:
                self.cover(j.col)
                if step_mode:
                    self.current_solution = list(solution)
                    yield
                j = j.right

            yield from self.search(solution, step_mode=step_mode)

            solution.pop()
            j = r.left
            while j != r:
                self.uncover(j.col)
                if step_mode:
                    self.current_solution = list(solution)
                    yield
                j = j.left

            r = r.down

        self.uncover(c)
        if step_mode:
            self.current_solution = list(solution)
            yield

    def select_column(self):
        # Pick column with fewest 1s (smallest size)
        min_size = float('inf')
        best = None
        c = self.header.right
        while c != self.header:
            if c.size < min_size:
                min_size = c.size
                best = c
            c = c.right
        return best

    current_action = ""

    # Event handler functions for visualization
    def on_pick_column(self, col_node):
        self.current_action = f"Pick Column: {col_node.name}"
        self.current_column = col_node  # Save current column

    def on_pick_row(self, row_node):
        self.current_action = f"Pick Row: {row_node.row}"
        self.current_row = row_node  # Save current row

    def on_cover(self, col_node):
        self.current_action = f"Cover Column: {col_node.name}"

    def on_uncover(self, col_node):
        self.current_action = f"Uncover Column: {col_node.name}"




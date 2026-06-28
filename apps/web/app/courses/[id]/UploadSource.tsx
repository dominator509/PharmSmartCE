import React from "react";

type UploadSourceProps = {
  action: (formData: FormData) => Promise<void>;
  error?: string;
  notice?: string;
};

export function UploadSource({ action, error, notice }: UploadSourceProps) {
  return (
    <section style={styles.panel} aria-label="Upload source">
      <div style={styles.panelHeader}>
        <div>
          <h2 style={styles.title}>Upload source</h2>
          <p style={styles.body}>
            Submit a PDF or DOCX file for ingestion. The course source list
            updates after the upload completes.
          </p>
        </div>
      </div>

      {notice ? (
        <p style={styles.notice} role="status">
          {notice}
        </p>
      ) : null}
      {error ? (
        <p style={styles.error} role="alert">
          {error}
        </p>
      ) : null}

      <form action={action} encType="multipart/form-data" style={styles.form}>
        <label style={styles.label}>
          <span style={styles.labelText}>Source file</span>
          <input
            name="file"
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={styles.input}
          />
        </label>

        <button type="submit" style={styles.button}>
          Upload source
        </button>
      </form>
    </section>
  );
}

const styles: Record<string, React.CSSProperties> = {
  panel: {
    border: "1px solid #d7e0ea",
    borderRadius: 8,
    background: "#ffffff",
    padding: 18,
  },
  panelHeader: {
    display: "flex",
    alignItems: "flex-start",
    justifyContent: "space-between",
    gap: 12,
  },
  title: {
    margin: 0,
    fontSize: 20,
    lineHeight: 1.25,
  },
  body: {
    margin: "8px 0 0",
    lineHeight: 1.6,
    color: "#4b5b6d",
  },
  form: {
    display: "grid",
    gap: 12,
    marginTop: 16,
  },
  label: {
    display: "grid",
    gap: 6,
  },
  labelText: {
    fontSize: 13,
    fontWeight: 700,
    color: "#304255",
  },
  input: {
    width: "100%",
    maxWidth: 480,
    border: "1px solid #b9c6d4",
    borderRadius: 6,
    padding: "10px 12px",
    fontSize: 14,
    color: "#102033",
    background: "#ffffff",
  },
  button: {
    width: "fit-content",
    border: "1px solid #17385f",
    borderRadius: 6,
    padding: "10px 14px",
    background: "#17385f",
    color: "#ffffff",
    fontSize: 14,
    fontWeight: 700,
    cursor: "pointer",
  },
  notice: {
    margin: "12px 0 0",
    padding: "10px 12px",
    borderRadius: 6,
    background: "#e8f6ee",
    color: "#16613a",
    border: "1px solid #b9e1c9",
  },
  error: {
    margin: "12px 0 0",
    padding: "10px 12px",
    borderRadius: 6,
    background: "#fff0f0",
    color: "#9c1f1f",
    border: "1px solid #f2c1c1",
  },
};

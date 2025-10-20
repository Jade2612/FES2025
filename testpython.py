import pandas as pd
grn = pd.read_csv("G:/FES2025/grn_clean.csv")
invoice = pd.read_csv("G:/FES2025/invoice_lines (2).csv")
po = pd.read_csv("G:/FES2025/po_clean.csv")

po = po.rename(columns={'qty':'qty_po','price':'price_po'})
grn = grn.rename(columns={'qty':'qty_grn'})
invoice = invoice.rename(columns={'qty_billed' : 'qty_inv','unit_price_invoice' : 'price_inv'})

invoice['Duplicate'] = invoice.duplicated(subset=['invoice_no','po_no','sku'], keep=False)
invoice['Duplicate'] = invoice['Duplicate'].apply(lambda x: 'Duplicate' if x else '')
for col in ['invoice_no','po_no','sku']:
    invoice[col] = invoice[col].astype(str).str.strip()


invoice_po = invoice.merge(po, on=['po_no','sku'],how = 'left')
invoice_po['Price_Var'] = invoice_po.apply(
    lambda x: 'Price Variance' if pd.notna(x['price_inv']) and pd.notna(x['price_po']) and x['price_inv'] != x['price_po'] else '',
    axis=1
)
invoice_po['Qty_Var_PO'] = invoice_po.apply(
    lambda x: 'Qty Variance' if pd.notna(x['qty_inv']) and pd.notna(x['qty_po']) and x['qty_inv'] != x['qty_po'] else '', axis=1)

final = invoice_po.merge(grn[['po_no','sku','qty_grn']],on=['po_no','sku'], how = 'left')
final['Qty_Var_GRN'] = final.apply(
    lambda x: 'Qty Variance' if pd.notna(x['qty_inv']) and pd.notna(x['qty_grn']) and x['qty_inv'] != x['qty_grn'] else '', axis=1)
final.to_csv("G:/FES2025/lines_check.csv", index=False)

def get_status(row):
    flags = [row['Duplicate'], row['Price_Var'], row['Qty_Var_PO'], row['Qty_Var_GRN']]
    return 'REVIEW' if any(f != '' for f in flags) else 'MATCH'
final['Status'] = final.apply(get_status,axis = 1)

final.to_csv("G:/FES2025/result.csv", index=False)

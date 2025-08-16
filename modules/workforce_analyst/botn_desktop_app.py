#!/usr/bin/env python3
"""
🏢 BOTN Desktop Application
Professional Real Estate Deal Underwriting Assistant

Eliminates Flask/network issues by providing a native desktop interface
with direct Python integration for BOTN file creation.

Author: Claude Code Assistant (VITOR-WINGMAN)
Date: 2025-08-05
Version: 1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
import json
import os
import threading
from datetime import datetime
from pathlib import Path
import sys

# Import existing BOTN creator
try:
    from botn_file_creator_xlwings import BOTNFileCreatorXL
    XLWINGS_AVAILABLE = True
except ImportError:
    try:
        from botn_file_creator import BOTNFileCreator
        XLWINGS_AVAILABLE = False
    except ImportError:
        print("❌ No BOTN creator available")
        sys.exit(1)

class BOTNDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏢 BOTN Desktop - Real Estate Underwriting Assistant")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize BOTN creator
        if XLWINGS_AVAILABLE:
            self.botn_creator = BOTNFileCreatorXL()
            self.creator_type = "xlwings (Excel Compatible)"
        else:
            self.botn_creator = BOTNFileCreator()
            self.creator_type = "standard"
        
        # Cache directory
        self.cache_dir = "/Users/vitorfaroni/Library/CloudStorage/Dropbox-HERR/Vitor Faroni/Colosseum/modules/workforce_analyst/deal_cache"
        
        # Data storage
        self.deals_data = {}
        self.selected_deal = None
        
        # Setup UI
        self.setup_styles()
        self.create_widgets()
        self.load_deals()
        
    def setup_styles(self):
        """Setup custom styles for professional appearance"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), background='#f0f0f0')
        style.configure('Info.TLabel', font=('Helvetica', 10), background='#f0f0f0')
        style.configure('Success.TLabel', font=('Helvetica', 10), background='#f0f0f0', foreground='#27ae60')
        style.configure('Error.TLabel', font=('Helvetica', 10), background='#f0f0f0', foreground='#e74c3c')
        
        # Button styles
        style.configure('Primary.TButton', font=('Helvetica', 10, 'bold'))
        style.configure('Success.TButton', font=('Helvetica', 10, 'bold'))
        
    def create_widgets(self):
        """Create the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🏢 BOTN Desktop - Real Estate Underwriting Assistant", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Left panel - Deal selection
        self.create_deal_selection_panel(main_frame)
        
        # Right panel - Deal details and actions
        self.create_deal_details_panel(main_frame)
        
        # Bottom panel - Status and actions
        self.create_status_panel(main_frame)
        
    def create_deal_selection_panel(self, parent):
        """Create the deal selection panel"""
        # Deal selection frame
        deal_frame = ttk.LabelFrame(parent, text="📊 Available Deals", padding="10")
        deal_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        deal_frame.rowconfigure(1, weight=1)
        
        # Refresh button
        refresh_btn = ttk.Button(deal_frame, text="🔄 Refresh", command=self.load_deals)
        refresh_btn.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Deal listbox with scrollbar
        listbox_frame = ttk.Frame(deal_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        listbox_frame.rowconfigure(0, weight=1)
        listbox_frame.columnconfigure(0, weight=1)
        
        self.deal_listbox = tk.Listbox(listbox_frame, font=('Helvetica', 10))
        self.deal_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.deal_listbox.bind('<<ListboxSelect>>', self.on_deal_select)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.deal_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.deal_listbox.yview)
        
        # Deal count label
        self.deal_count_label = ttk.Label(deal_frame, text="", style='Info.TLabel')
        self.deal_count_label.grid(row=2, column=0, pady=(10, 0), sticky=tk.W)
        
    def create_deal_details_panel(self, parent):
        """Create the deal details panel"""
        # Details frame
        details_frame = ttk.LabelFrame(parent, text="🏠 Deal Details", padding="10")
        details_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        details_frame.rowconfigure(0, weight=1)
        details_frame.columnconfigure(0, weight=1)
        
        # Scrolled text for deal details
        self.details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, font=('Courier', 10))
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # BOTN creation button
        self.create_botn_btn = ttk.Button(details_frame, text="🎯 Create BOTN File", 
                                         command=self.create_botn_threaded, 
                                         style='Success.TButton',
                                         state='disabled')
        self.create_botn_btn.grid(row=1, column=0, pady=(10, 0), sticky=tk.E)
        
    def create_status_panel(self, parent):
        """Create the status panel"""
        # Status frame
        status_frame = ttk.LabelFrame(parent, text="📋 Status", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        status_frame.columnconfigure(1, weight=1)
        
        # Creator type info
        creator_label = ttk.Label(status_frame, text=f"BOTN Creator: {self.creator_type}", style='Info.TLabel')
        creator_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", style='Info.TLabel')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Batch creation button
        batch_btn = ttk.Button(status_frame, text="🚀 Create All BOTNs", 
                              command=self.create_all_botns_threaded,
                              style='Primary.TButton')
        batch_btn.grid(row=0, column=2, sticky=tk.E)
        
    def load_deals(self):
        """Load deals from cache directory"""
        self.update_status("Loading deals...")
        self.deals_data.clear()
        self.deal_listbox.delete(0, tk.END)
        
        if not os.path.exists(self.cache_dir):
            self.update_status("❌ Cache directory not found", is_error=True)
            return
        
        deal_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.cache_dir, filename)
                    with open(file_path, 'r') as f:
                        deal_data = json.load(f)
                    
                    deal_name = deal_data.get('deal_name', filename[:-5])
                    self.deals_data[deal_name] = deal_data
                    self.deal_listbox.insert(tk.END, deal_name)
                    deal_count += 1
                    
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        self.deal_count_label.config(text=f"📊 {deal_count} deals loaded")
        self.update_status(f"✅ Loaded {deal_count} deals")
        
    def on_deal_select(self, event):
        """Handle deal selection"""
        selection = self.deal_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        deal_name = self.deal_listbox.get(index)
        self.selected_deal = deal_name
        
        # Display deal details
        self.display_deal_details(deal_name)
        
        # Enable BOTN creation button
        self.create_botn_btn.config(state='normal')
        
    def display_deal_details(self, deal_name):
        """Display detailed information about selected deal"""
        if deal_name not in self.deals_data:
            return
            
        deal_data = self.deals_data[deal_name]['data']
        
        # Clear and populate details
        self.details_text.delete(1.0, tk.END)
        
        details = f"""🏠 PROPERTY DETAILS
{'='*50}

Property Name: {deal_data.get('Property Name', 'N/A')}
Address: {deal_data.get('Address', 'N/A')}
City: {deal_data.get('City', 'N/A')}, {deal_data.get('State', 'N/A')} {deal_data.get('Zip Code', 'N/A')}
Year Built: {deal_data.get('Year Built', 'N/A')}

📊 UNIT INFORMATION
{'='*50}

Total Units: {deal_data.get('Number of Units', deal_data.get('Total Units', 'N/A'))}
Studio Units: {deal_data.get('# Studio Units', 'N/A')}
1-Bed Units: {deal_data.get('# 1 Bed Units', 'N/A')}
2-Bed Units: {deal_data.get('# 2 Bed Units', 'N/A')}
3-Bed Units: {deal_data.get('# 3 Bed Units', 'N/A')}

💰 FINANCIAL INFORMATION
{'='*50}

Average In-Place Rent: {deal_data.get('Avg In Place Rents', 'N/A')}
Studio Rent: {deal_data.get('Studio Rents', 'N/A')}
1-Bed Rent: {deal_data.get('1 Bed Current Rents', 'N/A')}
2-Bed Rent: {deal_data.get('2 Bed Current Rents', 'N/A')}
3-Bed Rent: {deal_data.get('3 Bed Current Rents', 'N/A')}

T12 Net Rental Income: ${deal_data.get('T12 Net Rental Income', 'N/A')}
T12 Other Income: ${deal_data.get('T12 Total Other Income', 'N/A')}
T12 Expenses: ${deal_data.get('T12 Expenses', 'N/A')}
T12 RUBS Income: ${deal_data.get('T12 RUBS Income', 'N/A')}

📍 LOCATION
{'='*50}

County: {deal_data.get('County Name', 'N/A')}

📅 DATA INFO
{'='*50}

Extracted: {self.deals_data[deal_name].get('extracted_date', 'N/A')}
Version: {self.deals_data[deal_name].get('version', 'N/A')}
"""
        
        self.details_text.insert(1.0, details)
        
    def create_botn_threaded(self):
        """Create BOTN file in separate thread to avoid UI blocking"""
        if not self.selected_deal:
            messagebox.showwarning("Warning", "Please select a deal first")
            return
            
        # Start creation in separate thread
        thread = threading.Thread(target=self.create_single_botn, args=(self.selected_deal,))
        thread.daemon = True
        thread.start()
        
    def create_single_botn(self, deal_name):
        """Create BOTN file for single deal"""
        try:
            self.update_status(f"🏗️ Creating BOTN for {deal_name}...")
            self.create_botn_btn.config(state='disabled')
            
            deal_data = self.deals_data[deal_name]['data']
            result = self.botn_creator.create_botn_file(deal_name, deal_data)
            
            if result["success"]:
                self.update_status(f"✅ BOTN created: {result['filename']}", is_success=True)
                messagebox.showinfo("Success", 
                                  f"BOTN file created successfully!\n\n"
                                  f"File: {result['filename']}\n"
                                  f"Location: {result['folder']}")
            else:
                self.update_status(f"❌ BOTN creation failed: {result['error']}", is_error=True)
                messagebox.showerror("Error", f"Failed to create BOTN file:\n{result['error']}")
                
        except Exception as e:
            error_msg = f"❌ Error creating BOTN: {str(e)}"
            self.update_status(error_msg, is_error=True)
            messagebox.showerror("Error", f"Error creating BOTN file:\n{str(e)}")
        finally:
            self.create_botn_btn.config(state='normal')
            
    def create_all_botns_threaded(self):
        """Create BOTN files for all deals in separate thread"""
        if not self.deals_data:
            messagebox.showwarning("Warning", "No deals loaded")
            return
            
        result = messagebox.askyesno("Confirm", 
                                   f"Create BOTN files for all {len(self.deals_data)} deals?\n\n"
                                   f"This may take several minutes...")
        if not result:
            return
            
        # Start batch creation in separate thread
        thread = threading.Thread(target=self.create_all_botns)
        thread.daemon = True
        thread.start()
        
    def create_all_botns(self):
        """Create BOTN files for all deals"""
        total_deals = len(self.deals_data)
        successful = 0
        failed = 0
        
        self.update_status(f"🚀 Creating {total_deals} BOTN files...")
        
        for i, (deal_name, deal_info) in enumerate(self.deals_data.items(), 1):
            try:
                self.update_status(f"🏗️ Creating BOTN {i}/{total_deals}: {deal_name}...")
                
                deal_data = deal_info['data']
                result = self.botn_creator.create_botn_file(deal_name, deal_data)
                
                if result["success"]:
                    successful += 1
                    print(f"✅ {deal_name} → {result['filename']}")
                else:
                    failed += 1
                    print(f"❌ {deal_name} → Failed: {result['error']}")
                    
            except Exception as e:
                failed += 1
                print(f"❌ {deal_name} → Error: {str(e)}")
        
        # Show completion message
        self.update_status(f"✅ Batch complete: {successful} success, {failed} failed", is_success=True)
        
        messagebox.showinfo("Batch Creation Complete", 
                          f"BOTN Creation Results:\n\n"
                          f"✅ Successful: {successful}\n"
                          f"❌ Failed: {failed}\n"
                          f"📊 Total: {total_deals}\n\n"
                          f"Files saved to: ~/Deals/[Deal Name]/BOTN/")
        
    def update_status(self, message, is_success=False, is_error=False):
        """Update status label with message"""
        def update_ui():
            self.status_label.config(text=message)
            if is_success:
                self.status_label.config(style='Success.TLabel')
            elif is_error:
                self.status_label.config(style='Error.TLabel')
            else:
                self.status_label.config(style='Info.TLabel')
        
        # Schedule UI update in main thread
        self.root.after(0, update_ui)

def main():
    """Main application entry point"""
    print("🏢 Starting BOTN Desktop Application...")
    print("=" * 50)
    
    # Check if xlwings is available
    if XLWINGS_AVAILABLE:
        print("✅ Using xlwings for Excel compatibility")
    else:
        print("⚠️ xlwings not available, using standard creator")
    
    # Create and run application
    root = tk.Tk()
    app = BOTNDesktopApp(root)
    
    print("🚀 BOTN Desktop Application ready!")
    print("📋 Features:")
    print("   • No network dependencies")
    print("   • Direct Python BOTN creation")
    print("   • Professional desktop interface")
    print("   • Batch processing support")
    print("=" * 50)
    
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
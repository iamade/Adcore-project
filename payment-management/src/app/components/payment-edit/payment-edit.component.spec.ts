import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditPaymentComponent } from './payment-edit.component';

describe('PaymentEditComponent', () => {
  let component: EditPaymentComponent;
  let fixture: ComponentFixture<EditPaymentComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditPaymentComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EditPaymentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
